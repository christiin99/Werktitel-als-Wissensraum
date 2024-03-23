# Dieser Code ist genauso in Jupyter abgelegt, falls er nicht funktioniert,
# kann die main.py gestartet werden

import pandas as pd  # Bibliothek zum Einlesen der Excel-Datei als Pandas-Dataframe
import plotly.graph_objs as go  # Bibliothek zum Visualisieren der Daten
import plotly.express as px  # Bibliothek zum Visualisieren der Daten für interaktive Plots
import dash  # grundlegendes Hauptmodul für das Erstellen der Dash-Anwendung
from dash import dcc, html, Input, Output  # dcc für Dropdowns, html für darauf basierende Komponenten, die in
# Dash-Anwendungen verwendet werden können, Input und Output für Callbacks
import random  # Bibliothek zur Generierung von zufälligen Werten in Verbindung mit der Werksuche-Funktion
from fuzzywuzzy import process  # Bibliothek um String-Matching von Werten (hier: Namen von Autor*innen)
# in Verbindung mit der Werksuche-Funktion durchzuführen

# Suchfeld
# Pfad zur Excel-Datei; diese laden
excel_datei_pfad = "Datensatz-Werktitel-Stand-10-07.xlsx"

# Daten aus der Excel-Datei lesen und leere Zeilen löschen - für Thema 1 (Werksuche)
df2 = pd.read_excel(excel_datei_pfad).dropna(subset=["Autor"])

# Alle anderen Themen
# Die Excel-Datei einlesen
df = pd.read_excel("Datensatz-Werktitel-Stand-10-07.xlsx")

# Duplikate aus den Spalten "Geschlecht", "Autor", "Nationalität", "Gattung" und "Wirkungsort" entfernen
df_unique = df.drop_duplicates(subset=["Autor", "Nationalität", "Geschlecht", "Gattung", "Wirkungsort"])

# Top 11 Länder Zusatz - für Thema 2 (Gattungsverteilung)
unique_authors = df.drop_duplicates(subset=["Autor", "Geschlecht", "Nationalität", "Gattung"])
# Anzahl der einzelnen Autor*innen pro Gattung zählen
genre_counts = unique_authors["Gattung"].value_counts()
# Farbsequenz für die Diagramme
colors = ["#DDBFA9", "#FF9642", "#00CED1", "#ECD540", "#FFC0CB", "#FFFF66", "#85e0db",
          "#FF7F50", "#98FB98", "#87CEEB", "#8BD3E6", "#E6E6FA", "#98FB98", "#FA8072",
          "#CCCCFF", "#FFFACD", "#008080", "#FFFDD0", "#C8A2C8", "#F0FFF0", "#FADADD"]
# Kreisdiagramm erstellen
fig = go.Figure(data=go.Pie(labels=genre_counts.index, values=genre_counts.values, hole=0.3))
# Layout anpassen
fig.update_layout(
    title="Gattungsverteilung nach Geschlecht",  # Titel
    annotations=[  # Textgestaltung und -positionierung, Pfeil/Strich nicht anzeigen
        dict(text="Männlich", x=0.2, y=0.5, font_size=12, showarrow=False),
        dict(text="Weiblich", x=0.8, y=0.5, font_size=12, showarrow=False)
    ]
)
fig.update_traces(marker=dict(colors=colors))  # Farben aktualisieren

# Ländernamen aus Excel-Tabelle und ISO-Ländercodes kombinieren
country_mapping = {
    "Argentinien": "ARG",
    "Armenien": "ARM",
    "Australien": "AUS",
    "Belarus": "BLR",
    "Belgien": "BEL",
    "Bulgarien": "BGR",
    "Dänemark": "DNK",
    "Deutschland": "DEU",
    "Dominikanische Republik": "DOM",
    "Estland": "EST",
    "Finnland": "FIN",
    "Frankreich": "FRA",
    "Griechenland": "GRC",
    "Iran": "IRN",
    "Irland": "IRL",
    "Island": "ISL",
    "Israel": "ISR",
    "Italien": "ITA",
    "Japan": "JPN",
    "Kanada": "CAN",
    "Kroatien": "HRV",
    "Kuba": "CUB",
    "Liechtenstein": "LIE",
    "Litauen": "LTU",
    "Luxemburg": "LUX",
    "Mexiko": "MEX",
    "Niederlande": "NLD",
    "Norwegen": "NOR",
    "Österreich": "AUT",
    "Palästina": "PSE",
    "Polen": "POL",
    "Rumänien": "ROU",
    "Russland": "RUS",
    "Schweden": "SWE",
    "Schweiz": "CHE",
    "Serbien": "SRB",
    "Slovakei": "SVK",
    "Slovenien": "SVN",
    "Spanien": "ESP",
    "Syrien": "SYR",
    "Südkorea": "KOR",
    "Türkei": "TUR",
    "Tschechien": "CZE",
    "Ukraine": "UKR",
    "Ungarn": "HUN",
    "Vatikan": "VAT",
    "Vereinigte Staaten": "USA",
    "Vereinigtes Königreich": "GBR"
}

# Städtenamen des Datensatzes mit Koordinaten der Städte verknüpfen
city_coordinates = {
    "Berlin": (52.5200, 13.4050),
    "München": (48.1372, 11.5755),
    "Leipzig": (51.3396, 12.3713),
    "Hamburg": (53.5511, 9.9937),
    "Köln": (50.9375, 6.9603),
    "Frankfurt am Main": (50.1109, 8.6821),
    "Dresden": (51.0504, 13.7373),
    "Freiburg im Breisgau": (47.9990, 7.8421),
    "Halle (Saale)": (51.4826, 11.9646),
    "Heidelberg": (49.3988, 8.6724)
}

# Erstelle Dash-App
# App wird als Dash-App erstellt
app = dash.Dash(__name__, assets_folder="assets")

# Setze die Konfiguration, um Callback-Ausnahmen zu unterdrücken
app.config.suppress_callback_exceptions = True

# Hauptmenü Layout
# Div-Container mit Hauptmenü-Elementen wird erstellt
main_menu_layout = html.Div([

    # Überschrift "Werktitel Projekt" wird erstellt und gestaltet
    html.H1("Werktitel Projekt", className="header"),

    # Div-Container mit Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Button "Werksuche" wird erstellt und gestaltet
        html.Button("Werksuche", id="button-theme1", className="topnav button"),

        # Button "Gattungsverteilung" wird erstellt und gestaltet
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav button"),

        # Button "Karte der deutschen Städte" wird erstellt und gestaltet
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav button"),

        # Button "Weltkarte" wird erstellt und gestaltet
        html.Button("Weltkarte", id="button-theme4", className="topnav button"),

        # Button "Kreisdiagramme" wird erstellt
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),

        # Button "Balkendiagramme" wird erstellt
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),  # Stil für den Div-Container wird definiert

    # Untere Überschrift "Über das Projekt" wird erstellt und gestaltet
    html.H3("Über das Projekt", className="footer"),

    html.Div([
        "Herzlich Willkommen! Wir haben den Datensatz \"Werktitel als Wissensraum\" vom DLA Marbach und der",
        html.Br(),
        "Herzogin Anna Amalia Bibliothek zur Verfügung gestellt bekommen, analysiert und visualisiert."
    ], className="p"),

    # Bild wird mit Quelle, Alternativtext und Stil erstellt
    html.Img(
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Johann_Heinrich_Wilhelm_Tischbein_-_Goethe_in_der_roemischen_Campagna.jpg/1024px-Johann_Heinrich_Wilhelm_Tischbein_-_Goethe_in_der_roemischen_Campagna.jpg",
        alt="Goethe",
        className="bild"),

    # Div-Container mit Text und Stil wird erstellt
    html.Div("Goethe in Italien",
             className="bildunterschrift"),


    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023", className="textfusszeile")
    ], className="fußzeile")
])

# Thema 1 - Werksuche Layout
# Div-Container für Thema 1 wird erstellt
theme1_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Link "Zurück zum Hauptmenü" wird erstellt und gestaltet
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),

        # Button "Werksuche" wird erstellt
        html.Button("Werksuche", id="button-theme1", className="topnav"),

        # Button "Gattungsverteilung" wird erstellt
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),

        # Button "Karte der deutschen Städte" wird erstellt
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),

        # Button "Weltkarte" wird erstellt
        html.Button("Weltkarte", id="button-theme4", className="topnav"),

        # Button "Kreisdiagramme" wird erstellt
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),

        # Button "Balkendiagramme" wird erstellt
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),  # Stil für den Div-Container wird definiert

    # Weitere Überschrift "Autor*innen und ihre Werke" wird erstellt und gestaltet
    html.H1("Autor*innen und ihre Werke", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Eingabefeld für Autorname wird erstellt und gestaltet
    dcc.Input(id="autor-eingabe", type="text", placeholder="Namen eingeben", className="input-field"),

    # Div-Container für Ausgabe wird erstellt
    html.Div(id="ausgabe", className="output-field"),

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


# Callback-Funktion, die auf Benutzerinteraktionen reagiert und Ausgabewerte für das Layout generiert
@app.callback(
    Output("ausgabe", "children"),  # Definiert die Ausgabe, die in das "ausgabe" Element eingefügt wird
    [Input("autor-eingabe", "value")]  # Nimmt den Wert des Eingabefelds "autor-eingabe" als Input
)
def suche_titel(autorname):  # Funktion wird mit dem eingegebenen Autorname-Argument aufgerufen
    if autorname:  # Wenn ein Autorname vorhanden ist
        autorname = autorname.strip().lower()  # Leerzeichen entfernen und in Kleinbuchstaben konvertieren
        # Datenframe nach dem eingegebenen Autornamen filtern
        filtered_df2 = df2[df2["Autor"].str.strip().str.lower() == autorname]
        if filtered_df2.empty:  # Wenn keine exakte Übereinstimmung gefunden wurde
            # Ähnliche Autorennamen basierend auf dem eingegebenen Namen suchen
            aehnliche_autoren = process.extract(autorname, df2["Autor"], limit=5)  # Limit der Vorschläge: 5
            vorschlaege = [vorschlag[0] for vorschlag in aehnliche_autoren]  # Liste ähnlicher Autorennamen erstellen
            vorschlaege = list(set(vorschlaege))  # Duplikate entfernen
            if len(vorschlaege) == 0:  # Wenn keine ähnlichen Autorennamen gefunden wurden
                return None  # Keine Ergebnisse zurückgeben
            # Rückgabe einer Liste ähnlicher Autorennamen als HTML-Elemente
            return html.Div([
                html.P("Keine Titel gefunden. Ähnliche Namen:"),
                html.Ul([html.Li(vorschlag) for vorschlag in vorschlaege])
            ])
        else:  # Wenn exakte Übereinstimmung gefunden wurde
            titel = filtered_df2["Titel"]  # Titel des/der Autor*in aus dem gefilterten Dataframe extrahieren
            anzahl_titel = len(titel)  # Anzahl der gefundenen Titel zählen
            if anzahl_titel > 0:  # Wenn mindestens ein Titel gefunden wurde
                # Titel in eine Liste von HTML-Listenelementen umwandeln und zurückgeben
                titel_liste = [html.Li(t) for t in titel]
                return [
                    html.P(f"Anzahl der Titel: {anzahl_titel}"),  # Anzahl der gefundenen Titel anzeigen
                    html.Ul(titel_liste)  # Liste der gefundenen Titel als HTML-Liste zurückgeben
                ]
            else:  # Wenn keine Titel gefunden wurden
                return "Keine Titel gefunden."
    else:  # Wenn kein Autorname eingegeben wurde
        autoren_liste = random.sample(df2["Autor"].tolist(), 5)  # Zufällige Auswahl von 5 Autorennamen
        return html.Div([
            html.P("Hier wären ein paar Vorschläge von Autor*innen:"),  # Nachricht für die zufälligen Autorennamen
            html.Ul([html.Li(autor) for autor in autoren_liste])  # Zufällige Autorennamen als Liste zurückgeben
        ])


# Thema 2 - Gattungsverteilung Layout
# Div-Container für Thema 2 wird erstellt
theme2_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Link "Zurück zum Hauptmenü" wird erstellt und gestaltet
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),

        # Buttons für verschiedene Themen werden erstellt
        html.Button("Werksuche", id="button-theme1", className="topnav"),
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),
        html.Button("Weltkarte", id="button-theme4", className="topnav"),
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),  # Stil für den Div-Container wird definiert

    # Weitere Überschrift "Top 11 Länder: Gattungsverteilung nach Geschlecht" wird erstellt und gestaltet
    html.H1("Top 11 Länder: Gattungsverteilung nach Geschlecht", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Dropdown-Menü für die Auswahl der Länder wird erstellt und gestaltet
    html.P("Länder", className="label"),
    dcc.Dropdown(
        id="names",
        options=[
            # Liste von Ländern und ihren Werten für das Dropdown-Menü
            # Hier sind Beispiele von Ländern aufgeführt, die angepasst werden können
            {"label": "Deutschland", "value": "Deutschland"},
            {"label": "Frankreich", "value": "Frankreich"},
            {"label": "Österreich", "value": "Österreich"},
            {"label": "Schweiz", "value": "Schweiz"},
            {"label": "Vereinigte Staaten ", "value": "Vereinigte Staaten"},
            {"label": "Vereinigtes Königreich", "value": "Vereinigtes Königreich"},
            {"label": "Österreich-Ungarn", "value": "Österreich-Ungarn"},
            {"label": "Italien", "value": "Italien"},
            {"label": "Russland", "value": "Russland"},
            {"label": "Ungarn", "value": "Ungarn"},
            {"label": "Dänemark", "value": "Dänemark"}
        ],
        value="Deutschland",  # Standardwert des Dropdown-Menüs
        clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
        className="dropdown"  # Stil für das Dropdown-Menü wird definiert
    ),

    # Dropdown-Menü für die Auswahl des Geschlechts wird erstellt und gestaltet
    html.Div([
        html.Label(["Geschlecht"], className="label"),  # Label für das Dropdown-Menü
        dcc.Dropdown(
            id="gender_dropdown",
            options=[
                # Optionen für Geschlecht
                {"label": "Gesamt", "value": "Gesamt"},
                {"label": "Männlich", "value": "Männlich"},
                {"label": "Weiblich", "value": "Weiblich"},
            ],
            value="Gesamt",  # Standardwert des Dropdown-Menüs
            multi=False,  # Es kann nur eine Option ausgewählt werden
            clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
            style={"width": "50%"},  # Stil für die Dropdown-Breite wird festgelegt
            className="dropdown"  # Stil für das Dropdown-Menü wird definiert
        ),
    ], className="dropdown-container"),  # Stil für den Div-Container des Dropdown-Menüs wird definiert

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Diagramm wird erstellt und gestaltet
    dcc.Graph(id="graph", className="chart"),

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


# Callback-Funktion, die ein Kreisdiagramm für ausgewählte Länder und Geschlechter generiert
@app.callback(
    Output("graph", "figure"),  # Ausgabe des Kreisdiagramms in das "graph" Element
    Input("names", "value"), Input("gender_dropdown", "value"),  # Eingaben für ausgewählte Länder und Geschlechter
)
def generate_chart(names, gender_dropdown):
    # Daten basierend auf ausgewählten Optionen filtern
    if names == "Deutschland":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Deutschland"]
    elif names == "Frankreich":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Frankreich"]
    elif names == "Österreich":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Österreich"]
    elif names == "Schweiz":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Schweiz"]
    elif names == "Vereinigte Staaten ":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Vereinigte Staaten "]
    elif names == "Finnland":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Finnland"]
    elif names == "Vereinigtes Königreich":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Vereinigtes Königreich"]
    elif names == "Österreich-Ungarn":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Österreich-Ungarn"]
    elif names == "Italien":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Italien"]
    elif names == "Ungarn":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Ungarn"]
    elif names == "Dänemark":
        filtered_data = unique_authors[unique_authors["Nationalität"] == "Dänemark"]
    else:
        filtered_data = unique_authors  # Default: alle Daten werden verwendet

    if gender_dropdown == "Männlich":
        filtered_data = filtered_data[filtered_data["Geschlecht"] == "Männlich"]
    elif gender_dropdown == "Weiblich":
        filtered_data = filtered_data[filtered_data["Geschlecht"] == "Weiblich"]

    # Gattungen zählen
    genre_counts_filtered = filtered_data["Gattung"].value_counts()

    # Kreisdiagramm generieren
    fig = go.Figure(data=go.Pie(labels=genre_counts_filtered.index, values=genre_counts_filtered.values, hole=0.3))
    fig.update_layout(title=f"Gattungsverteilung nach Geschlecht - {names}")
    fig.update_traces(marker=dict(colors=colors))

    if genre_counts_filtered.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Keine Daten verfügbar für {gender_dropdown} in {names}",
            showlegend=False
        )
        fig.add_annotation(
            # Wenn keine Daten vorhanden sind, soll ein Hinweis erscheinen
            text="Bitte wählen Sie eine andere Kombination aus.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18)
        )
    else:
        fig = go.Figure(data=go.Pie(labels=genre_counts_filtered.index, values=genre_counts_filtered.values, hole=0.3))
        fig.update_layout(title=f"Gattungsverteilung nach Geschlecht - {names}")
        fig.update_traces(marker=dict(colors=colors))

    return fig  # Generiertes Kreisdiagramm zurückgeben


# Thema 3 Layout
# Div-Container für Thema 3 wird erstellt
theme3_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Link "Zurück zum Hauptmenü" wird erstellt und gestaltet
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),

        # Buttons für verschiedene Themen werden erstellt
        html.Button("Werksuche", id="button-theme1", className="topnav"),
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),
        html.Button("Weltkarte", id="button-theme4", className="topnav"),
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),  # Stil für den Div-Container wird definiert

    # Weitere Überschrift "Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Karte)" wird erstellt
    html.H1("Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Karte)", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Dropdown-Menü zur Auswahl der Karte wird erstellt und gestaltet
    html.Div([
        html.Label("Karte auswählen", className="label"),  # Label für das Dropdown-Menü
        dcc.Dropdown(
            id="map_dropdown",  # ID für das Dropdown-Menü wird festgelegt
            options=[  # Optionen für das Dropdown-Menü
                {"label": "Wirkungsort der Autor*innen", "value": "Wirkungsort"},
                {"label": "Wirkungsort der Autor*innen (Gattung: Epik)", "value": "Epik"},
                {"label": "Wirkungsort der Autor*innen (Gattung: Drama)", "value": "Drama"},
                {"label": "Wirkungsort der Autor*innen (Gattung: Lyrik)", "value": "Lyrik"}
            ],
            value="Wirkungsort",  # Standardwert des Dropdown-Menüs
            clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
            className="dropdown"  # Stil für das Dropdown-Menü wird definiert
        ),
    ], className="dropdown-container"),  # Stil für den Div-Container des Dropdown-Menüs wird definiert

    # Dropdown-Menü zur Auswahl des Geschlechts wird erstellt und gestaltet
    html.Div([
        html.Label("Geschlecht auswählen", className="label"),  # Label für das Dropdown-Menü
        dcc.Dropdown(
            id="gender_dropdown",  # ID für das Dropdown-Menü wird festgelegt
            options=[  # Optionen für das Dropdown-Menü
                {"label": "Gesamt", "value": "Gesamt"},
                {"label": "Männlich", "value": "Männlich"},
                {"label": "Weiblich", "value": "Weiblich"}
            ],
            value="Gesamt",  # Standardwert des Dropdown-Menüs
            clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
            className="dropdown"  # Stil für das Dropdown-Menü wird definiert
        ),
    ], className="dropdown-container"),  # Stil für den Div-Container des Dropdown-Menüs wird definiert

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Grafikfeld für die Karte wird erstellt und gestaltet
    dcc.Graph(id="bubble_map", className="chart"),  # ID und Stil für das Karten-Grafikfeld

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


# Callback-Funktion, die auf Auswahl der Benutzer*innen in Dropdown-Menüs reagiert
@app.callback(
    Output("bubble_map", "figure"),  # filtert Datenframe basierend auf Auswahl/Input der Benutzer*innen
    [Input("map_dropdown", "value"),
     Input("gender_dropdown", "value")]
)
# Funktionsaufruf, wenn sich Werte der beiden Dropdown-Menüs ändern
def update_bubble_map(selected_map, selected_gender):
    # Gewünschte Städte filtern
    cities = ["Berlin", "München", "Leipzig", "Hamburg", "Köln", "Frankfurt am Main", "Dresden", "Freiburg im Breisgau",
              "Halle (Saale)", "Heidelberg"]
    df_filtered = df_unique[df_unique["Wirkungsort"].isin(cities)]

    # Funktion filtert Datenframe df basierend auf dem ausgewählten Geschlecht
    if selected_gender == "Gesamt":
        df_selected = df_filtered.copy()  # Funktion behält gesamten Datenframe
    elif selected_gender == "Männlich":
        # nur Zeilen mit Geschlecht männlich im Datenframe enthalten
        df_selected = df_filtered[df_filtered["Geschlecht"] == "Männlich"]
    elif selected_gender == "Weiblich":
        # nur Zeilen mit Geschlecht weiblich im Datenframe enthalten
        df_selected = df_filtered[df_filtered["Geschlecht"] == "Weiblich"]

    # Nach Wirkungsorten gruppieren und Autor*innen zählen / Anzahl der Autor*innen pro Wirkungsort
    if selected_map == "Wirkungsort":  # zählt Anzahl der Autor*innen pro Wirkungsort
        city_counts = df_selected["Wirkungsort"].value_counts().reset_index()
        title = "Verteilung der Autor*innen auf ausgewählte Städte in Deutschland"  # Titel
        if selected_gender == "Weiblich":
            size_multiplier = 7  # vergrößern der Blasen, da sonst nicht sichtbar
        else:
            size_multiplier = 1  # Größe kann so bleiben
    elif selected_map == "Epik":  # zählt Anzahl der Autor*innen der Epik pro Wirkungsort
        df_epik = df_selected[df_selected["Gattung"] == "Epik"]
        city_counts = df_epik["Wirkungsort"].value_counts().reset_index()
        title = "Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Gattung: Epik)"
        size_multiplier = 7  # vergrößern der Blasen, da sonst nicht sichtbar
    elif selected_map == "Drama":  # zählt Anzahl der Autor*innen des Dramas pro Wirkungsort
        df_drama = df_selected[df_selected["Gattung"] == "Drama"]
        city_counts = df_drama["Wirkungsort"].value_counts().reset_index()
        title = "Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Gattung: Drama)"
        size_multiplier = 7  # vergrößern der Blasen, da sonst nicht sichtbar
    elif selected_map == "Lyrik":  # zählt Anzahl der Autor*innen der Lyrik pro Wirkungsort
        df_lyrik = df_selected[df_selected["Gattung"] == "Lyrik"]
        city_counts = df_lyrik["Wirkungsort"].value_counts().reset_index()
        title = "Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Gattung: Lyrik)"
        size_multiplier = 7  # vergrößern der Blasen, da sonst nicht sichtbar

    city_counts.columns = ["Wirkungsort", "Autor"]

    # Bubble-Diagramm erstellen
    fig = go.Figure()  # leeres Objekt

    for city in city_counts["Wirkungsort"]:  # Schleife geht durch jeden Wirkungsort
        count = city_counts.loc[city_counts["Wirkungsort"] == city, "Autor"].iloc[0]
        latitude, longitude = city_coordinates[city]  # mithilfe von Breiten- und Längengrad aus city_coordinates erhalten
        bubble_size = count * size_multiplier  # Größe der Blasen anpassen, size_multiplier in vorherigen Bedingungen
        sizeref = 2 * max(city_counts["Autor"]) / (bubble_size ** 2)  # Größenbezug definieren
        fig.add_trace(  # leeres Objekt wird befüllt
            go.Scattergeo(  # Erstellung der Karte / Bestimmung der Eigenschaften der Blasen
                lon=[longitude],  # setzt Längengrade auf im vorherigen Schritt ermittelte Werte
                lat=[latitude],  # setzt Breitengrade auf im vorherigen Schritt ermittelte Werte
                mode="markers",  # Aussehen der Blasen
                marker=dict(  # Beschreibung der Markereigenschaften
                    size=bubble_size,  # Größe der Blasen
                    sizemode="diameter",  # Größe als Durchmesser
                    sizeref=sizeref,  # oben festgelegte Größe verwenden
                    color=bubble_size,  # Anzahl Autor*innen wird verwendet für Farben auf Karte
                    line=dict(width=0.5, color="white")  # Linienbreite und Farbe für Markierungen
                ),
                text=f"{city}<br>Autor*innen: {count}",  # angezeigter Text, wenn man mit Maus über Blasen fährt (interaktiv)
                name=city  # Name der Blasen (Wirkungsort), der in Legende des Diagramms angezeigt wird
            )
        )

    # Layout anpassen
    fig.update_layout(
        title=title,  # Titel der Karte
        geo=dict(  # geografische Eigenschaften
            scope="europe",  # Karte auf Europa beschränkt
            lonaxis_range=[5.5, 15.5],  # Bereich der angezeigten Längengrade
            lataxis_range=[47, 55],  # Bereich der angezeigten Breitengrade
            showland=True,  # Land anzeigen (Deutschland)
            landcolor="rgb(229, 229, 229)",  # Farben des Landes
            countrycolor="rgb(255, 255, 255)",  # Farben der Ländergrenzen
            coastlinecolor="rgb(255, 255, 255)",  # Farben der Küstenlinien
            showocean=False,  # Ozean nicht anzeigen
            showrivers=False,  # Flüsse nicht anzeigen
            resolution=50,  # Auflösung der Karte
            projection_type="mercator"  # Übersetzung: Projektionsart
        ),
        showlegend=True,  # Legende anzeigen
        legend=dict(  # Eigenschaften der Legende
            traceorder="normal",  # Reihenfolge der Wirkungsorte (nach Größe in Legende angezeigt)
            font=dict(family="sans-serif", size=12, color="black"),  # Schriftart, -größe, -farbe
            bgcolor="rgba(0,0,0,0)",  # Hintergrundfarben der Legende
            bordercolor="rgba(0,0,0,0)"  # Randfarbe der Legende
        )
    )

    # Wenn keine Daten vorhanden sind, Hinweis anzeigen
    if city_counts.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Keine Daten verfügbar für diese Kombination",
            showlegend=False
        )
        fig.add_annotation(
            text="Bitte wählen Sie eine andere Kombination aus.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18)
        )

    return fig  # Funktion als Ausgabe zurückgeben


# Thema 4 Layout
# Div-Container für Thema 4 wird erstellt
theme4_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Link "Zurück zum Hauptmenü" wird erstellt und gestaltet
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),

        # Buttons für verschiedene Themen werden erstellt
        html.Button("Werksuche", id="button-theme1", className="topnav"),
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),
        html.Button("Weltkarte", id="button-theme4", className="topnav"),
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),  # Stil für den Div-Container wird definiert

    # Weitere Überschrift "Verteilung der Nationalitäten von Autor*innen" wird erstellt
    html.H1("Verteilung der Nationalitäten von Autor*innen", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Dropdown-Menü zur Auswahl der Karte wird erstellt und gestaltet
    html.Div([
        html.Label("Karte auswählen", className="label"),  # Label für das Dropdown-Menü
        dcc.Dropdown(
            id="map_dropdown",  # ID für das Dropdown-Menü wird festgelegt
            options=[  # Optionen für das Dropdown-Menü
                {"label": "Nationalitäten", "value": "Autor"},
                {"label": "Gattung Epik", "value": "Epik"},
                {"label": "Gattung Drama", "value": "Drama"},
                {"label": "Gattung Lyrik", "value": "Lyrik"}
            ],
            value="Autor",  # Standardwert des Dropdown-Menüs
            clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
            className="dropdown"  # Stil für das Dropdown-Menü wird definiert
        ),
    ], className="dropdown-container"),  # Stil für den Div-Container des Dropdown-Menüs wird definiert

    # Dropdown-Menü zur Auswahl des Geschlechts wird erstellt und gestaltet
    html.Div([
        html.Label("Geschlecht auswählen", className="label"),  # Label für das Dropdown-Menü
        dcc.Dropdown(
            id="gender_dropdown",  # ID für das Dropdown-Menü wird festgelegt
            options=[  # Optionen für das Dropdown-Menü
                {"label": "Gesamt", "value": "Gesamt"},
                {"label": "Männlich", "value": "Männlich"},
                {"label": "Weiblich", "value": "Weiblich"}
            ],
            value="Gesamt",  # Standardwert des Dropdown-Menüs
            clearable=False,  # Möglichkeit, das Dropdown-Feld zu leeren, ist deaktiviert
            className="dropdown"  # Stil für das Dropdown-Menü wird definiert
        ),
    ], className="dropdown-container"),  # Stil für den Div-Container des Dropdown-Menüs wird definiert

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Grafikfeld für die Karte wird erstellt und gestaltet
    dcc.Graph(id="choropleth_map", className="chart"),  # ID und Stil für das Karten-Grafikfeld

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


# Callback-Funktion, die auf Auswahl der Benutzer*innen in Dropdown-Menüs reagiert
@app.callback(
    Output("choropleth_map", "figure"),  # filtert Datenframe basierend auf Auswahl/Input der Benutzer*innen
    [Input("map_dropdown", "value"),
     Input("gender_dropdown", "value")]
)
# Funktionsaufruf, wenn sich Werte der beiden Dropdown-Menüs ändern
def update_choropleth_map(selected_map, selected_gender):
    # Funktion filtert Datenframe df basierend auf dem ausgewählten Geschlecht
    if selected_gender == "Gesamt":
        df_selected = df_unique.copy()  # Funktion behält gesamten Datenframe
    elif selected_gender == "Männlich":
        df_selected = df_unique[df_unique["Geschlecht"] == "Männlich"]  # nur Zeilen mit Geschlecht männlich im Datenframe enthalten
    elif selected_gender == "Weiblich":
        df_selected = df_unique[df_unique["Geschlecht"] == "Weiblich"]  # nur Zeilen mit Geschlecht weiblich im Datenframe enthalten

    # Ländercodes/Standardisierte Ländernamen der Karte hinzufügen
    df_selected["iso_alpha"] = df_selected["Nationalität"].map(country_mapping)

    # Funktion filtert Datenframe df basierend auf der ausgewählten Karte
    if selected_map == "Autor":  # zählt Anzahl der Autor*innen pro Land
        df_counts = df_selected.groupby("iso_alpha")["Autor"].count().reset_index()
        title = "Verteilung der Nationalitäten von Autor*innen"  # Titel
        range_color = (0, 100)  # Wertebereich und mittleren Punkt je nach Gattung individuell anpassen
        color_continuous_midpoint = 50
    elif selected_map == "Epik":  # zählt Anzahl der Autor*innen der Epik pro Land
        df_epik = df_selected[df_selected["Gattung"] == "Epik"]
        df_counts = df_epik.groupby("iso_alpha")["Autor"].count().reset_index()
        title = "Verteilung der Nationalitäten von Autor*innen der Gattung Epik"
        range_color = (0, 100)
        color_continuous_midpoint = 50
    elif selected_map == "Drama":  # zählt Anzahl der Autor*innen des Dramas pro Land
        df_drama = df_selected[df_selected["Gattung"] == "Drama"]
        df_counts = df_drama.groupby("iso_alpha")["Autor"].count().reset_index()
        title = "Verteilung der Nationalitäten von Autor*innen der Gattung Drama"
        range_color = (0, 100)
        color_continuous_midpoint = 50
    elif selected_map == "Lyrik":  # zählt Anzahl der Autor*innen der Lyrik pro Land
        df_lyrik = df_selected[df_selected["Gattung"] == "Lyrik"]
        df_counts = df_lyrik.groupby("iso_alpha")["Autor"].count().reset_index()
        title = "Verteilung der Nationalitäten von Autor*innen der Gattung Lyrik"
        range_color = (0, 100)
        color_continuous_midpoint = 50

    # Funktion erstellt Choroplethenkarte
    fig = px.choropleth(
        df_counts,
        locations="iso_alpha",  # welche Spalte des Datenframe die geografischen Standorte enthält
        locationmode="ISO-3",  # Ländercodes im ISO-3-Format, also drei-buchstabige Kürzel
        color="Autor",  # Spalte Autor*innen des Datenframes wird verwendet für die Farben auf der Karte
        hover_name="iso_alpha",  # ISO-Ländercodes anzeigen, wenn Benutzer*in mit Maus über Region auf Karte fährt
        title=title,  # Titel der Karte, in jeder Bedingung oben individuell angepasst
        color_continuous_scale="tropic",  # Farbpalette der Choroplethenkarte bestimmen
        range_color=range_color,  # Bereich der Werte für die Farbskala optimieren, in jeder Bedingung oben individuell
        color_continuous_midpoint=color_continuous_midpoint  # mittlerer Punkt der Farbskala (individuell)
    )

    return fig  # Funktion als Ausgabe zurückgeben


# Thema 5 Layout
# Div-Container für Thema 5 wird erstellt
theme5_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([

        # Link "Zurück zum Hauptmenü" wird erstellt und gestaltet
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),

        # Buttons für verschiedene Themen werden erstellt
        html.Button("Werksuche", id="button-theme1", className="topnav"),
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),
        html.Button("Weltkarte", id="button-theme4", className="topnav"),
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),

    # Überschrift "Kreisdiagramme" wird erstellt
    html.H1("Kreisdiagramme", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Dropdown-Menü zur Auswahl des Diagramms wird erstellt und gestaltet
    html.Div([
        html.Label("Werktitel als Wissensraum", className="label"),  # Titel
        dcc.Dropdown(  # 1. Dropdown-Menü zur Auswahl des Diagramms
            id="my_dropdown",  # ID wird verwendet, um im Callback auf Dropdown-Menü zu verweisen
            options=[  # Optionen des Dropdown-Menüs
                {"label": "Nationalität der Autor*innen", "value": "Nationalität"},
                {"label": "Sprache der Veröffentlichung", "value": "Sprache der Veröffentlichung"},
                {"label": "Geschlecht", "value": "Geschlecht"},
                {"label": "Gattung", "value": "Gattung"},
                {"label": "Wirkungsort", "value": "Wirkungsort"},
            ],
            value="Geschlecht",  # Anfangswert des Dropdown-Menüs
            multi=False,  # bestimmt, ob Benutzer*innen mehrere Werte aus Dropdown-Menü auswählen kann oder (hier: nicht)
            clearable=False,  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            style={"width": "50%"},  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            className="dropdown"
        ),
    ], className="dropdown-container"),
    html.Div([
        html.Label("Geschlecht auswählen", className="label"),  # Titel
        dcc.Dropdown(  # 2. Dropdown-Menü zur Auswahl des Geschlechts
            id="gender_dropdown",
            options=[  # Optionen des Dropdown-Menüs
                {"label": "Gesamt", "value": "Gesamt"},
                {"label": "Männlich", "value": "Männlich"},
                {"label": "Weiblich", "value": "Weiblich"}
            ],
            value="Gesamt",  # Anfangswert des Dropdown-Menüs
            multi=False,  # bestimmt, ob Benutzer*innen mehrere Werte aus Dropdown-Menü auswählen kann oder (hier: nicht)
            clearable=False,  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            style={"width": "50%"},  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            className="dropdown"
        ),
    ], className="dropdown-container"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Grafikfeld für das Diagramm wird erstellt und gestaltet
    dcc.Graph(id="the_graph_1", className="chart"),  # ID und Stil des Grafikfelds

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


# Grenze (threshold) festlegen, unter der alle Werte zur besseren Übersichtlichkeit in Andere fallen
def group_values_below_threshold(df_unique, column, threshold):
    counts = df_unique[column].value_counts()
    below_threshold = counts[counts / counts.sum() < threshold].index
    df_unique[column] = df_unique[column].apply(lambda x: "Andere" if x in below_threshold else x)
    return df_unique  # "angepassten" Datenframe zurückgeben


# Callback-Funktion, die auf Auswahl der Benutzer*innen in Dropdown-Menüs reagiert
@app.callback(
    Output(component_id="the_graph_1", component_property="figure"),  # filtert Datenframe basierend auf Auswahl/Input der Benutzer*innen
    [Input(component_id="my_dropdown", component_property="value"),
     Input(component_id="gender_dropdown", component_property="value")]
)
# Funktionsaufruf, wenn sich Werte der beiden Dropdown-Menüs ändern
def update_graph(my_dropdown, gender_dropdown):
    # Funktion filtert Datenframe df basierend auf dem ausgewählten Geschlecht
    if gender_dropdown == "Gesamt":
        dff = df_unique.dropna(subset=[my_dropdown])
    else:
        dff = df_unique[(df_unique["Geschlecht"] == gender_dropdown)].dropna(subset=[my_dropdown])  # nur Zeilen behalten, in denen
        # Geschlecht gleich "gender_dropdown" ist

    # Alle Werte einer Kategorie fallen unter Andere, wenn sie unter 1 % liegen
    dff = group_values_below_threshold(dff, my_dropdown, 0.01)

    # Farbsequenz für die Diagramme
    colors = ["#DDBFA9", "#FF9642", "#00CED1", "#ECD540", "#FFC0CB", "#FFFF66", "#85e0db",
              "#FF7F50", "#98FB98", "#87CEEB", "#8BD3E6", "#E6E6FA", "#98FB98", "#FA8072",
              "#CCCCFF", "#FFFACD", "#008080", "#FFFDD0", "#C8A2C8", "#F0FFF0", "#FADADD"]

    # Funktion erstellt Kreisdiagramm
    piechart = px.pie(
        data_frame=dff,  # Datenframe dff als Eingabe für die Funktion
        names=my_dropdown,  # Spalte "my_dropdown" aus dff wird für Erstellung der Labels für die Sektoren des Kreisdiagramms verwendet
        hole=0.3,  # Erzeugen eines Lochs mit einem Durchmesser von 0.3 in der Mitte des Kreisdiagramms
        color=my_dropdown,  # Spalte für die Farbcodierung der Balken
        color_discrete_sequence=colors,  # Benutzerdefinierte Farbsequenz
    )
    return piechart  # Funktion als Ausgabe zurückgeben


# Thema 6 Layout
# Div-Container für Thema 6 wird erstellt
theme6_layout = html.Div([

    # Überschrift "Hauptmenü" wird erstellt und gestaltet
    html.H1("Hauptmenü", className="header"),

    # Div-Container mit Links und Buttons für verschiedene Themen wird erstellt
    html.Div([
        html.A("Zurück zum Hauptmenü", href="/", className="topnav button button-link"),
        html.Button("Werksuche", id="button-theme1", className="topnav"),
        html.Button("Gattungsverteilung", id="button-theme2", className="topnav"),
        html.Button("Karte der deutschen Städte", id="button-theme3", className="topnav"),
        html.Button("Weltkarte", id="button-theme4", className="topnav"),
        html.Button("Kreisdiagramme", id="button-theme5", className="topnav"),
        html.Button("Balkendiagramme", id="button-theme6", className="topnav")
    ], className="topnav"),

    # Überschrift "Balkendiagramme" wird erstellt
    html.H1("Balkendiagramme", className="Überschrift"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Dropdown-Menü zur Auswahl des Diagramms wird erstellt und gestaltet
    html.Div([
        html.Label("Werktitel als Wissensraum", className="label"),  # Titel
        dcc.Dropdown(  # 1. Dropdown-Menü zur Auswahl der Gattung
            id="my_dropdown",  # ID wird verwendet, um im Callback auf Dropdown-Menü zu verweisen
            options=[  # Optionen des Dropdown-Menüs
                {"label": "Nationalität der Autor*innen", "value": "Nationalität"},
                {"label": "Sprache der Veröffentlichung", "value": "Sprache der Veröffentlichung"},
                {"label": "Geschlecht", "value": "Geschlecht"},
                {"label": "Gattung", "value": "Gattung"},
                {"label": "Wirkungsort", "value": "Wirkungsort"},
            ],
            value="Geschlecht",  # Anfangswert des Dropdown-Menüs
            multi=False,  # bestimmt, ob Benutzer*innen mehrere Werte aus Dropdown-Menü auswählen kann oder (hier: nicht)
            clearable=False,  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            style={"width": "50%"},  # Aussehen der Dropdown-Komponente
            className="dropdown"
        ),
    ], className="dropdown-container"),

    # Dropdown-Menü zur Auswahl des Diagramms wird erstellt und gestaltet
    html.Div([
        html.Label("Geschlecht auswählen", className="label"),  # Titel
        dcc.Dropdown(  # 2. Dropdown-Menü zur Auswahl des Geschlechts
            id="gender_dropdown",  # ID wird verwendet, um im Callback auf Dropdown-Menü zu verweisen
            options=[  # Optionen des Dropdown-Menüs
                {"label": "Gesamt", "value": "Gesamt"},
                {"label": "Männlich", "value": "Männlich"},
                {"label": "Weiblich", "value": "Weiblich"}
            ],
            value="Gesamt",  # Anfangswert des Dropdown-Menüs
            multi=False,  # bestimmt, ob Benutzer*innen mehrere Werte aus Dropdown-Menü auswählen kann oder (hier: nicht)
            clearable=False,  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            style={"width": "50%"},  # Aussehen der Dropdown-Komponente
            className="dropdown"
        ),
    ], className="dropdown-container"),

    # Dropdown-Menü zur Auswahl der Darstellung/Skalierung des Diagramms wird erstellt und gestaltet
    html.Div([
        html.Label("Skalierung auswählen", className="label"),  # Titel
        dcc.Dropdown(  # 2. Dropdown-Menü zur Auswahl des Geschlechts
            id="log_dropdown",  # ID wird verwendet, um im Callback auf Dropdown-Menü zu verweisen
            options=[  # Optionen des Dropdown-Menüs
                {"label": "Linear", "value": "Linear"},
                {"label": "Logarithmisch", "value": "Logarithmisch"}
            ],
            value="Linear",  # Anfangswert des Dropdown-Menüs
            multi=False,  # bestimmt, ob Benutzer*innen mehrere Werte aus Dropdown-Menü auswählen kann oder (hier: nicht)
            clearable=False,  # Parameter bestimmt, dass Benutzer*innen ausgewählten Wert im Dropdown-Menü nicht löschen kann
            style={"width": "50%"},  # Aussehen der Dropdown-Komponente
            className="dropdown"
        ),
    ], className="dropdown-container"),

    # Zeilenumbruch wird eingefügt
    html.Br(),

    # Grafikfeld für das Diagramm wird erstellt und gestaltet
    dcc.Graph(id="the_graph_2", className="chart"),  # Grafikfeld, in dem das Diagramm angezeigt wird

    # Div-Container der Fußzeile wird erstellt
    html.Div([
        html.P("Erstellt von Aylin Acilanmak, Martina Schorsten & Christin Walter | © 2023",
               id="fußzeile",
               className="fußzeile_2")
    ])
])


def get_absolute_counts(df_unique, column):  # Funktion, damit im Balkendiagramm absolute Zahlen angezeigt werden, zählt jede
    # Spalte, die in einem Datenframe gezählt wird
    counts = df_unique[column].value_counts().reset_index()
    counts.columns = [column, "Count"]
    return counts  # gibt Datenframe zurück


# Callback-Funktion, die auf Auswahl der Benutzer*innen in Dropdown-Menüs reagiert
@app.callback(
    Output(component_id="the_graph_2", component_property="figure"),  # filtert Datenframe basierend auf Auswahl/Input der Benutzer*innen
    [Input(component_id="my_dropdown", component_property="value"),
     Input(component_id="gender_dropdown", component_property="value"),
     Input(component_id="log_dropdown", component_property="value")]
)
# Funktionsaufruf, wenn sich Werte der beiden Dropdown-Menüs ändern
def update_graph(my_dropdown, gender_dropdown, log_dropdown):
    # Funktion filtert Datenframe df basierend auf dem ausgewählten Geschlecht
    if gender_dropdown == "Gesamt":
        dff = df_unique.dropna(subset=[my_dropdown])
    else:
        dff = df_unique[(df_unique["Geschlecht"] == gender_dropdown)].dropna(subset=[my_dropdown])  # nur Zeilen behalten, in denen
        # Geschlecht gleich "gender_dropdown" ist

    # absolute Zahlen und nur die TOP 50 Werte sollen angezeigt werden, falls es mehr als 50 gibt
    counts = get_absolute_counts(dff, my_dropdown).head(50)

    # Farbsequenz für die Diagramme
    colors = ["#DDBFA9", "#FF9642", "#00CED1", "#ECD540", "#FFC0CB", "#FFFF66", "#85e0db",
              "#FF7F50", "#98FB98", "#87CEEB", "#8BD3E6", "#E6E6FA", "#98FB98", "#FA8072",
              "#CCCCFF", "#FFFACD", "#008080", "#FFFDD0", "#C8A2C8", "#F0FFF0", "#FADADD"]

    # Funktion erstellt Balkendiagramm
    barchart = px.bar(
        data_frame=counts,  # Datenframe, der Daten für das Balkendiagramm enthält
        x=my_dropdown,  # Spalte, die auf x-Achse dargestellt werden soll
        y="Count",  # Spalte, die auf y-Achse dargestellt werden soll
        color=my_dropdown,  # Spalte für die Farbcodierung der Balken
        color_discrete_sequence=colors,  # Benutzerdefinierte Farbsequenz
        labels={my_dropdown: my_dropdown, "Count": "Count"}  # Achsenbeschriftung
    )

    # Überprüfen Sie den Wert des log_dropdown und passen Sie die Achsenskalierung an
    if log_dropdown == "Linear":
        barchart.update_layout(yaxis_type="linear")
    elif log_dropdown == "Logarithmisch":
        barchart.update_layout(yaxis_type="log")

    return barchart  # Funktion als Ausgabe zurückgeben


# Layout der App
# Div-Container wird erstellt und gestaltet
app.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ],

    # seperates CSS-stylesheet gibt die Stil-Definitionen
    # der eingebundenen html-Container vor
    # Basierend darauf, lässt sich somit das gesamte Aussehen der App verändern
    style={"link": {"href": "assets/Hauptmenü.css", "rel": "stylesheet"}}
)


# Callback-Funktion für das Umschalten zwischen den Seiten
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return main_menu_layout  # Aktualisiert den angezeigten Inhalt entsprechend der ausgewählten Seite
    elif pathname == "/Autor*innen und ihre Werke":
        return theme1_layout  # Zeigt das Layout für Autor*innen und ihre Werke an
    elif pathname == "/Top 11 Länder: Gattungsverteilung nach Geschlecht":
        return theme2_layout  # Zeigt das Layout für die Gattungsverteilung nach Geschlecht an
    elif pathname == "/Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Karte)":
        return theme3_layout  # Zeigt das Layout für die Verteilung auf Städte in Deutschland an
    elif pathname == "/Verteilung der Nationalitäten von Autor*innen":
        return theme4_layout  # Zeigt das Layout für die Verteilung der Nationalitäten an
    elif pathname == "/Kreisdiagramme":
        return theme5_layout  # Zeigt das Layout für Kreisdiagramme an
    elif pathname == "/Balkendiagramme":
        return theme6_layout  # Zeigt das Layout für Balkendiagramme an
    else:
        return main_menu_layout  # Zeigt das Hauptmenü-Layout an


# Callback-Funktionen für die Button-Klicks
@app.callback(
    dash.dependencies.Output("url", "pathname"),
    dash.dependencies.Input("button-theme1", "n_clicks"),
    dash.dependencies.Input("button-theme2", "n_clicks"),
    dash.dependencies.Input("button-theme3", "n_clicks"),
    dash.dependencies.Input("button-theme4", "n_clicks"),
    dash.dependencies.Input("button-theme5", "n_clicks"),
    dash.dependencies.Input("button-theme6", "n_clicks")
)
def update_page_url(n_clicks_theme1, n_clicks_theme2, n_clicks_theme3, n_clicks_theme4, n_clicks_theme5, n_clicks_theme6):
    if n_clicks_theme1:
        return "/Autor*innen und ihre Werke"  # Aktualisiert die URL, wenn der erste Button geklickt wird
    elif n_clicks_theme2:
        return "/Top 11 Länder: Gattungsverteilung nach Geschlecht"  # Aktualisiert die URL, wenn der zweite Button geklickt wird
    elif n_clicks_theme3:
        return "/Verteilung der Autor*innen auf ausgewählte Städte in Deutschland (Karte)"  # Aktualisiert die URL, wenn der dritte Button geklickt wird
    elif n_clicks_theme4:
        return "/Verteilung der Nationalitäten von Autor*innen"  # Aktualisiert die URL, wenn der vierte Button geklickt wird
    elif n_clicks_theme5:
        return "/Kreisdiagramme"  # Aktualisiert die URL, wenn der fünfte Button geklickt wird
    elif n_clicks_theme6:
        return "/Balkendiagramme"  # Aktualisiert die URL, wenn der sechste Button geklickt wird
    else:
        return "/"  # Setzt die URL zurück auf die Startseite, wenn kein Button geklickt wurde


# App starten
if __name__ == "__main__":
    app.run_server(debug=True)  # Startet die App im Debug-Modus
