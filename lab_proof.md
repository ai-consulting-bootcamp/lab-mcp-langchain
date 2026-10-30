# Lab Proof: World Bank Data360 mit MCP und LangChain

## Ziel und Implementierung

Das Notebook [mcp_langchain.ipynb](mcp_langchain.ipynb) verbindet einen LangChain-Agenten mit dem ?ffentlichen World Bank Data360 MCP-Server. Der Agent soll Indikatoren suchen und seine Antworten auf tats?chlich zur?ckgegebene Daten st?tzen.

Dieser Nachweis basiert auf den im Notebook gespeicherten Ausgaben. F?r die Erstellung dieses Dokuments wurden keine neuen Modell- oder Datenabfragen ausgef?hrt.

## Workflow

1. Der OpenAI-Key wird mit `python-dotenv` aus der Umgebung geladen, ohne ihn auszugeben.
2. `MultiServerMCPClient` konfiguriert `https://maimcpext.worldbank.org/ext/data360/mcp` mit `transport="http"` f?r Streamable HTTP.
3. `session.list_tools()` und `session.list_resources()` entdecken die Server-F?higkeiten. Die gespeicherte Ausgabe von `client.get_tools()` best?tigt: `Loaded 16 LangChain tools.` Die Objekte werden mit `BaseTool` gepr?ft.
4. `ChatOpenAI` verwendet `gpt-4o-mini` mit `temperature=0`. `create_agent` erh?lt Modell, Tools und Anweisungen zur datenbasierten Beantwortung.
5. In Step 5 werden `data360://system-prompt` und `data360://context` gelesen und ihre Textbl?cke in den Agenten-Prompt aufgenommen. Der gespeicherte Runtime-Kontext enth?lt `current_date: 2026-10-30` und `current_year: 2026`.
6. `agent.ainvoke()` f?hrt die Abfrage mit `recursion_limit=30` aus. Die Trace-Zellen zeigen Tool-Namen, Argumente und Antworten. Explizite Ressourcen-Sessions werden durch `async with` geschlossen.

Die erste Bev?lkerungsabfrage unten wurde vor dem Einbinden der Ressourcen ausgef?hrt. Nach Step 5 zeigt das Notebook eine erneute Bev?lkerungsantwort mit demselben Wert; daf?r ist kein eigener vollst?ndiger Trace gespeichert. Ressourcenintegration und urspr?nglicher Datenabruf sind damit getrennt belegt.

## Eine nachvollziehbare Abfrage

Die Query in Step 4 lautet:

> Find the latest available population total for Germany using World Bank Data360. Include the indicator, year, unit, and source.

### 1. Indikator suchen

Der gespeicherte Trace zeigt:

```python
data360_search_indicators(
    query="population total",
    required_country="DEU"
)
```

Die Suchantwort enth?lt unter anderem folgenden Treffer (Auszug):

```json
{
  "idno": "WB_WDI_SP_POP_TOTL",
  "database_id": "WB_WDI",
  "name": "Population, total",
  "latest_data": "2025",
  "covers_country": {"DEU": true}
}
```

Der anschlie?end verwendete Indikator stammt somit aus einem Suchergebnis und wurde nicht nur im Prompt vorgegeben.

### 2. Beobachtung abrufen

Der n?chste Tool-Aufruf lautet:

```python
data360_get_data(
    database_id="WB_WDI",
    indicator_id="WB_WDI_SP_POP_TOTL",
    country_code="DEU",
    year=2025
)
```

Die tats?chliche Tool-Antwort enth?lt folgende Beobachtung (Auszug):

```json
{
  "OBS_VALUE": "83491249",
  "UNIT_MULT": 0,
  "REF_AREA": "DEU",
  "TIME_PERIOD": "2025",
  "UNIT_MEASURE": "PS",
  "REF_AREA_NAME": "Germany",
  "UNIT_MEASURE_NAME": "Persons"
}
```

Die Metadaten nennen `Population, total` und `World Development Indicators (WDI)`. Das Tool liefert eine Beobachtung und `error: null`, allerdings auch einen Hinweis unter `failed_validation`: Der Filter `member_economies_only` wurde wegen des expliziten L?nderfilters nicht angewendet. Die Antwort ist deshalb nicht vollst?ndig warnungsfrei.

### 3. Gespeicherte finale Agentenantwort

```text
The latest available population total for Germany is as follows:

- **Indicator**: Population, total
- **Year**: 2025
- **Unit**: Persons
- **Source**: World Development Indicators (WDI)

The total population is projected to be **83,491,249** persons.
```

### Pr?fung der Belegkette

Wert, Land, Jahr, Einheit und Datenbank stimmen mit der Tool-Antwort ?berein. Die Formulierung ?projected? ist im gezeigten Daten- und Suchauszug jedoch nicht belegt. Ohne Pr?fung weiterer Metadaten sollte die Antwort neutral von einer zur?ckgegebenen Beobachtung sprechen.

Auch ?latest available? ist hier nur ?ber das Suchfeld `latest_data` und den Abruf f?r 2025 gest?tzt. Eine separate Pr?fung aller f?r Deutschland verf?gbaren Jahre ist in diesem Trace nicht enthalten.

## Beobachteter Fehlerfall: Nicht belegte Aufschl?sselungen

In Step 6 fragt eine weitere Query nach Deutschlands BIP pro Kopf seit 2010 sowie nach Aufschl?sselungen nach Geschlecht und Bundesland.

Die gespeicherte Trace-Ausgabe enth?lt die Suche nach `GDP per capita`, den Abruf von `WB_WDI_NY_GDP_PCAP_KD` f?r Deutschland von 2010 bis 2024 und `data360_get_disaggregation`.

Die Datenantwort enth?lt beispielsweise `38526.737104` f?r 2010 und `44027.763155` f?r 2024, jeweils in konstanten US-Dollar von 2015. Diese Werte stimmen gerundet mit der gespeicherten Agentenantwort ?berein.

Die Disaggregationsantwort nennt jedoch nur `REF_AREA`, `UNIT_MEASURE`, `TIME_PERIOD` und `REGION`; sie belegt weder eine Geschlechtsdimension noch deutsche Bundesl?nder. Trotzdem schl?gt der Agent solche Aufschl?sselungen sowie Alter und Bildungsniveau vor und bietet weitere Abrufe an.

Das ist eine konkrete Grounding-Schw?che: Die numerischen Werte k?nnen korrekt aus Tools stammen, w?hrend anschlie?ende Aussagen ?ber verf?gbare Daten unbelegt bleiben. BIP pro Kopf darf au?erdem nicht ohne Weiteres als individuelles Einkommen nach Geschlecht interpretiert werden.

Eine Verbesserung w?re, nur tats?chlich zur?ckgegebene Dimensionen als verf?gbar zu bezeichnen. Andere Analyseideen m?ssten ausdr?cklich als zus?tzliche Recherche mit anderen Indikatoren oder Quellen markiert werden. Diese Verbesserung wurde hier nicht implementiert oder erneut getestet.

## Reproduzierbarkeit und offene Punkte

- Die erste Installationszelle enth?lt noch Kommas in der Paketliste und hat einen gespeicherten Installationsfehler. F?r eine saubere Ausf?hrung muss sie lauten: `%pip install langchain langchain-openai langchain-mcp-adapters mcp python-dotenv`.
- Die gespeicherten Installationsausgaben melden einen Versionskonflikt zwischen dem nicht mehr ben?tigten `mcp-server-fetch` und dem vom Adapter verwendeten `mcp`. Eine frische Umgebung ohne Fetch vermeidet diese zus?tzliche Abh?ngigkeit; ein sauberer Neustart wurde f?r diesen Nachweis nicht durchgef?hrt.
- Die letzte Trace-Zelle zeigt BIP-Aufrufe, obwohl unmittelbar davor inzwischen eine Besch?ftigungsquery steht. Die gespeicherten Ausgaben sind daher nicht durchgehend in aktueller Zellreihenfolge erzeugt worden. Vor Abgabe sollten die passende Query und ihr Trace gemeinsam erneut ausgef?hrt und gespeichert werden.
- Die Besch?ftigungsantwort listet passende Indikatoren auf, zeigt aber noch keine vollst?ndige Analyse ihrer Entwicklung ?ber die Jahre.
- Der vollst?ndige Trace zur Bev?lkerungsfrage steht in Step 4 direkt nach der Query. Er bildet die prim?re Belegkette dieses Dokuments.

## Einordnung

Die gespeicherten Ausgaben belegen MCP-Verbindung, Tool-Entdeckung und Konvertierung, Ressourcenabruf und einen numerisch belegten Agentenlauf. Sie zeigen zugleich, dass Toolzugriff allein keine vollst?ndig belegte Interpretation garantiert. F?r eine Beratungsl?sung m?ssen Datenwerte, verf?gbare Dimensionen und sprachliche Schlussfolgerungen getrennt ?berpr?ft werden.
