"""
Tryxee Automations v2 — Visual Automation Designer
Expandable nodes · Theme toggle · Custom blocks · Port binding display
"""
import sys, math, json, uuid, os
from functools import reduce
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsEllipseItem, QGraphicsPathItem,
    QGraphicsDropShadowEffect, QMenu, QStatusBar,
    QMessageBox, QLineEdit,
    QSplitter, QTextEdit, QDialog,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QDialogButtonBox,
    QGraphicsItem
)
from PyQt5.QtCore import (
    Qt, QPointF, QRectF, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QObject, QRect
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QFont,
    QLinearGradient, QIcon, QPalette
)
import importlib.util
import importlib
import types

# ═══════════════════════════════════════════════════════════════════════════════
# THEME MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
class ThemeManager(QObject):
    changed = pyqtSignal()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._mode = "dark"
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._initialized = True

    @property
    def mode(self): return self._mode

    def toggle(self):
        self._mode = "light" if self._mode == "dark" else "dark"
        self.changed.emit()

    def is_dark(self): return self._mode == "dark"

TM = ThemeManager()

def C(dark_hex, light_hex=None):
    """Return a QColor depending on current theme."""
    if light_hex is None: light_hex = dark_hex
    return QColor(dark_hex if TM.is_dark() else light_hex)

class T:
    """Live theme colors — call as functions via C() or access via T.X."""
    @staticmethod
    def bg_deep():      return C("#0a0c10", "#f0f2f5")
    @staticmethod
    def bg_surface():   return C("#0f1218", "#e8eaed")
    @staticmethod
    def bg_panel():     return C("#131820", "#dde0e5")
    @staticmethod
    def bg_card():      return C("#1a2030", "#d0d4da")
    @staticmethod
    def border():       return C("#252d3d", "#b0b8c8")
    @staticmethod
    def border_light(): return C("#2e3a50", "#c0c8d8")
    @staticmethod
    def accent():       return C("#00d4ff", "#0088cc")
    @staticmethod
    def accent_dim():   return C("#0088aa", "#0066aa")
    @staticmethod
    def success():      return C("#10b981", "#059669")
    @staticmethod
    def warning():      return C("#f59e0b", "#d97706")
    @staticmethod
    def danger():       return C("#ef4444", "#dc2626")
    @staticmethod
    def info():         return C("#3b82f6", "#2563eb")
    @staticmethod
    def text_primary():   return C("#e8edf5", "#1a2030")
    @staticmethod
    def text_secondary(): return C("#7a8ba0", "#4a5568")
    @staticmethod
    def text_dim():       return C("#3d4f60", "#8090a8")
    @staticmethod
    def node_trigger():   return C("#7c3aed", "#6d28d9")
    @staticmethod
    def node_condition(): return C("#f59e0b", "#d97706")
    @staticmethod
    def node_action():    return C("#10b981", "#059669")
    @staticmethod
    def node_transform(): return C("#3b82f6", "#2563eb")
    @staticmethod
    def node_output():    return C("#ef4444", "#dc2626")
    @staticmethod
    def node_variable():  return C("#06b6d4", "#0891b2")
    @staticmethod
    def node_flow():      return C("#ec4899", "#db2777")
    @staticmethod
    def node_data():      return C("#84cc16", "#65a30d")
    @staticmethod
    def node_system():    return C("#f97316", "#ea580c")
    @staticmethod
    def node_network():   return C("#a78bfa", "#7c3aed")
    @staticmethod
    def node_custom():    return C("#fb7185", "#f43f5e")
    @staticmethod
    def cat_color(cat):
        return {
            "trigger":   T.node_trigger(),
            "condition": T.node_condition(),
            "action":    T.node_action(),
            "transform": T.node_transform(),
            "output":    T.node_output(),
            "variable":  T.node_variable(),
            "flow":      T.node_flow(),
            "data":      T.node_data(),
            "system":    T.node_system(),
            "network":   T.node_network(),
            "custom":    T.node_custom(),
        }.get(cat, T.accent())

# ═══════════════════════════════════════════════════════════════════════════════
# NODE CATALOG  (50+ nodes)
# ═══════════════════════════════════════════════════════════════════════════════
def _p(name, label, ptype, default, **kw):
    d = {"name": name, "label": label, "type": ptype, "default": default}
    d.update(kw)
    return d

NODE_CATALOG = [
    # ── TRIGGERS ──────────────────────────────────────────────────────────────
    {"id":"trigger_start",   "category":"trigger","title":"Démarrage","icon":"⚡",
     "description":"Point d'entrée du flux.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"}],
     "params":[_p("label","Étiquette","text","Démarrage"),_p("enabled","Activé","bool",True)]},
    {"id":"trigger_schedule","category":"trigger","title":"Planificateur","icon":"⏰",
     "description":"Déclenche le flux selon un planning.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"},{"name":"Timestamp","data_type":"string"}],
     "params":[_p("interval","Intervalle","number",60,min=1,max=86400),
               _p("unit","Unité","select","Minutes",options=["Secondes","Minutes","Heures","Jours"]),
               _p("enabled","Activé","bool",True)]},
    {"id":"trigger_webhook", "category":"trigger","title":"Webhook HTTP","icon":"🌐",
     "description":"Écoute les requêtes HTTP entrantes.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"},{"name":"Payload","data_type":"string"},{"name":"Headers","data_type":"string"}],
     "params":[_p("path","Chemin URL","text","/webhook"),
               _p("method","Méthode","select","POST",options=["GET","POST","PUT","DELETE","PATCH"]),
               _p("port","Port","number",8080,min=1,max=65535),
               _p("auth","Authentification","bool",False),
               _p("token","Token secret","text","")]},
    {"id":"trigger_file",    "category":"trigger","title":"Surveillance Fichier","icon":"📁",
     "description":"Surveille les modifications d'un fichier/dossier.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"},{"name":"Chemin","data_type":"string"},{"name":"Événement","data_type":"string"}],
     "params":[_p("path","Chemin","text","/chemin/vers/fichier"),
               _p("event","Événement","select","Modification",options=["Modification","Création","Suppression","Tous"]),
               _p("recursive","Récursif","bool",False),
               _p("pattern","Filtre (glob)","text","*")]},
    {"id":"trigger_interval","category":"trigger","title":"Minuterie","icon":"🔁",
     "description":"Émet un signal à intervalle régulier.",
     "inputs":[{"name":"Démarrer","type":"exec"},{"name":"Arrêter","type":"exec"}],
     "outputs":[{"name":"Tick","type":"exec"},{"name":"Compte","data_type":"number"}],
     "params":[_p("delay_ms","Délai (ms)","number",1000,min=10,max=3600000),
               _p("max_ticks","Ticks max (0=∞)","number",0,min=0,max=100000)]},
    {"id":"trigger_email_in","category":"trigger","title":"Réception Email","icon":"📨",
     "description":"Déclenche à la réception d'un email.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"},{"name":"De","data_type":"string"},{"name":"Sujet","data_type":"string"},{"name":"Corps","data_type":"string"}],
     "params":[_p("imap_host","Serveur IMAP","text","imap.gmail.com"),
               _p("port","Port","number",993,min=1,max=65535),
               _p("user","Utilisateur","text",""),
               _p("folder","Dossier","text","INBOX"),
               _p("unread_only","Non lus seulement","bool",True)]},
    {"id":"trigger_hotkey",  "category":"trigger","title":"Raccourci Clavier","icon":"⌨",
     "description":"Se déclenche sur un raccourci clavier global.",
     "inputs":[],"outputs":[{"name":"Exec","type":"exec"}],
     "params":[_p("keys","Combinaison","text","Ctrl+Alt+A"),
               _p("repeat","Répétition","bool",False)]},
    # ── CONDITIONS ────────────────────────────────────────────────────────────
    {"id":"cond_if",      "category":"condition","title":"Si / Sinon","icon":"◆",
     "description":"Branche selon une condition booléenne.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Condition","data_type":"bool"}],
     "outputs":[{"name":"Vrai","type":"exec"},{"name":"Faux","type":"exec"}],
     "params":[_p("label","Étiquette","text","Condition"),_p("invert","Inverser","bool",False)]},
    {"id":"cond_compare", "category":"condition","title":"Comparaison","icon":"⚖",
     "description":"Compare deux valeurs.",
     "inputs":[{"name":"A","data_type":"number"},{"name":"B","data_type":"number"}],
     "outputs":[{"name":"Résultat","data_type":"bool"}],
     "params":[_p("op","Opérateur","select","==",options=["==","!=",">",">=","<","<="]),
               _p("tol","Tolérance","float",0.0,min=0.0,max=1e6)]},
    {"id":"cond_filter",  "category":"condition","title":"Filtre","icon":"⧩",
     "description":"Filtre selon une expression.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Valeur","data_type":"any"}],
     "outputs":[{"name":"Valide","type":"exec"},{"name":"Invalide","type":"exec"}],
     "params":[_p("expr","Expression","text",""),
               _p("mode","Mode","select","Contient",options=["Regex","Contient","Égal","Commence par","Se termine par"]),
               _p("case","Sensible casse","bool",False)]},
    {"id":"cond_switch",  "category":"condition","title":"Switch / Case","icon":"⊕",
     "description":"Aiguille selon la valeur d'une entrée.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Valeur","data_type":"any"}],
     "outputs":[{"name":"Case 1","type":"exec"},{"name":"Case 2","type":"exec"},{"name":"Case 3","type":"exec"},{"name":"Défaut","type":"exec"}],
     "params":[_p("case1","Valeur Case 1","text","1"),
               _p("case2","Valeur Case 2","text","2"),
               _p("case3","Valeur Case 3","text","3")]},
    {"id":"cond_and",     "category":"condition","title":"ET logique","icon":"∧",
     "description":"Vrai si toutes les entrées sont vraies.",
     "inputs":[{"name":"A","data_type":"bool"},{"name":"B","data_type":"bool"},{"name":"C","data_type":"bool"}],
     "outputs":[{"name":"Résultat","data_type":"bool"}],
     "params":[]},
    {"id":"cond_or",      "category":"condition","title":"OU logique","icon":"∨",
     "description":"Vrai si au moins une entrée est vraie.",
     "inputs":[{"name":"A","data_type":"bool"},{"name":"B","data_type":"bool"}],
     "outputs":[{"name":"Résultat","data_type":"bool"}],
     "params":[]},
    {"id":"cond_not",     "category":"condition","title":"NON logique","icon":"¬",
     "description":"Inverse une valeur booléenne.",
     "inputs":[{"name":"Valeur","data_type":"bool"}],
     "outputs":[{"name":"Résultat","data_type":"bool"}],
     "params":[]},
    # ── FLOW CONTROL ──────────────────────────────────────────────────────────
    {"id":"flow_loop",    "category":"flow","title":"Boucle For","icon":"🔄",
     "description":"Répète un bloc N fois.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"N","data_type":"number"}],
     "outputs":[{"name":"Corps","type":"exec"},{"name":"Index","data_type":"number"},{"name":"Fin","type":"exec"}],
     "params":[_p("count","Itérations","number",10,min=1,max=100000),
               _p("start","Début","number",0,min=0),
               _p("step","Pas","number",1,min=1)]},
    {"id":"flow_foreach", "category":"flow","title":"Pour Chaque","icon":"📋",
     "description":"Itère sur chaque élément d'une liste.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Liste","data_type":"any"}],
     "outputs":[{"name":"Corps","type":"exec"},{"name":"Élément","data_type":"any"},{"name":"Index","data_type":"number"},{"name":"Fin","type":"exec"}],
     "params":[_p("separator","Séparateur (si string)","text",",")]},
    {"id":"flow_while",   "category":"flow","title":"Tant Que","icon":"↺",
     "description":"Répète tant que la condition est vraie.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Condition","data_type":"bool"}],
     "outputs":[{"name":"Corps","type":"exec"},{"name":"Fin","type":"exec"}],
     "params":[_p("max_iter","Iterations max","number",1000,min=1,max=1000000)]},
    {"id":"flow_trycatch","category":"flow","title":"Try / Catch","icon":"🛡",
     "description":"Capture les erreurs d'exécution.",
     "inputs":[{"name":"Exec","type":"exec"}],
     "outputs":[{"name":"Try","type":"exec"},{"name":"Catch","type":"exec"},{"name":"Erreur","data_type":"string"},{"name":"Finally","type":"exec"}],
     "params":[_p("reraise","Relancer l'erreur","bool",False)]},
    {"id":"flow_parallel","category":"flow","title":"Parallèle","icon":"⫼",
     "description":"Exécute plusieurs branches en parallèle.",
     "inputs":[{"name":"Exec","type":"exec"}],
     "outputs":[{"name":"Branche 1","type":"exec"},{"name":"Branche 2","type":"exec"},{"name":"Branche 3","type":"exec"}],
     "params":[_p("wait_all","Attendre toutes les branches","bool",True)]},
    {"id":"flow_gate",    "category":"flow","title":"Porte","icon":"🚪",
     "description":"Ouvre ou ferme le flux selon un état.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Ouvrir","type":"exec"},{"name":"Fermer","type":"exec"}],
     "outputs":[{"name":"Sortie","type":"exec"}],
     "params":[_p("init_open","Ouvert au démarrage","bool",True)]},
    {"id":"flow_delay",   "category":"flow","title":"Délai","icon":"⏳",
     "description":"Pause dans l'exécution.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Durée","data_type":"number"}],
     "outputs":[{"name":"Exec","type":"exec"}],
     "params":[_p("duration","Durée","number",5,min=0,max=3600),
               _p("unit","Unité","select","Secondes",options=["Ms","Secondes","Minutes"]),
               _p("random","Aléatoire","bool",False)]},
    # ── ACTIONS ───────────────────────────────────────────────────────────────
    {"id":"action_email", "category":"action","title":"Envoyer Email","icon":"✉",
     "description":"Envoie un email via SMTP.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Dest","data_type":"string"},{"name":"Sujet","data_type":"string"},{"name":"Corps","data_type":"string"}],
     "outputs":[{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("smtp_host","Serveur SMTP","text","smtp.gmail.com"),
               _p("smtp_port","Port","number",587,min=1,max=65535),
               _p("from","Expéditeur","text",""),_p("tls","TLS","bool",True)]},
    {"id":"action_http",  "category":"action","title":"Requête HTTP","icon":"🔗",
     "description":"Requête HTTP vers une URL.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"URL","data_type":"string"},{"name":"Body","data_type":"string"}],
     "outputs":[{"name":"Réponse","data_type":"string"},{"name":"Code","data_type":"number"},{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("method","Méthode","select","GET",options=["GET","POST","PUT","PATCH","DELETE"]),
               _p("timeout","Timeout (s)","number",30,min=1,max=300),
               _p("headers","Headers (JSON)","textarea",'{"Content-Type":"application/json"}'),
               _p("follow_redirect","Redirections","bool",True),
               _p("verify_ssl","Vérifier SSL","bool",True)]},
    {"id":"action_write_file","category":"action","title":"Écrire Fichier","icon":"💾",
     "description":"Écrit du contenu dans un fichier.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Chemin","data_type":"string"},{"name":"Contenu","data_type":"string"}],
     "outputs":[{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("mode","Mode","select","Écraser",options=["Écraser","Ajouter","Créer uniquement"]),
               _p("encoding","Encodage","select","UTF-8",options=["UTF-8","UTF-16","ASCII","Latin-1"]),
               _p("create_dirs","Créer dossiers","bool",True)]},
    {"id":"action_read_file","category":"action","title":"Lire Fichier","icon":"📄",
     "description":"Lit le contenu d'un fichier.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Chemin","data_type":"string"}],
     "outputs":[{"name":"Contenu","data_type":"string"},{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("encoding","Encodage","select","UTF-8",options=["UTF-8","UTF-16","ASCII","Latin-1"]),
               _p("lines_only","Lignes seulement","bool",False)]},
    {"id":"action_notification","category":"action","title":"Notification","icon":"🔔",
     "description":"Envoie une notification.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Titre","data_type":"string"},{"name":"Corps","data_type":"string"}],
     "outputs":[{"name":"Exec","type":"exec"}],
     "params":[_p("channel","Canal","select","Système",options=["Système","Slack","Discord","Teams","Telegram"]),
               _p("webhook_url","Webhook URL","text",""),
               _p("sound","Son","bool",True)]},
    {"id":"action_cmd",   "category":"action","title":"Commande Système","icon":"💻",
     "description":"Exécute une commande shell.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Cmd","data_type":"string"}],
     "outputs":[{"name":"Stdout","data_type":"string"},{"name":"Stderr","data_type":"string"},{"name":"Code","data_type":"number"},{"name":"Succès","type":"exec"}],
     "params":[_p("shell","Utiliser shell","bool",True),
               _p("timeout","Timeout (s)","number",60,min=0,max=3600),
               _p("cwd","Dossier courant","text","")]},
    {"id":"action_clipboard","category":"action","title":"Presse-papiers","icon":"📋",
     "description":"Lit ou écrit le presse-papiers.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Texte","data_type":"string"}],
     "outputs":[{"name":"Contenu","data_type":"string"},{"name":"Exec","type":"exec"}],
     "params":[_p("mode","Mode","select","Écrire",options=["Écrire","Lire","Les deux"])]},
    {"id":"action_db_query","category":"action","title":"Requête SQL","icon":"🗄",
     "description":"Exécute une requête sur une base de données.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Requête","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"any"},{"name":"Nb lignes","data_type":"number"},{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("db_type","SGBD","select","SQLite",options=["SQLite","PostgreSQL","MySQL","MSSQL"]),
               _p("host","Hôte","text","localhost"),_p("port","Port","number",5432,min=1,max=65535),
               _p("db","Base","text",""),_p("user","Utilisateur","text",""),
               _p("query","Requête par défaut","textarea","SELECT * FROM table")]},
    # ── TRANSFORMS ────────────────────────────────────────────────────────────
    {"id":"tf_format",    "category":"transform","title":"Formater Texte","icon":"Aa",
     "description":"Formate ou transforme du texte.",
     "inputs":[{"name":"Texte","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"string"}],
     "params":[_p("template","Template","textarea","Bonjour {0} !"),
               _p("case","Casse","select","Aucune",options=["Aucune","MAJUSCULES","minuscules","Titre","Inverse"]),
               _p("trim","Trim","bool",True)]},
    {"id":"tf_json_parse","category":"transform","title":"Parser JSON","icon":"{ }",
     "description":"Parse une chaîne JSON.",
     "inputs":[{"name":"JSON","data_type":"string"}],
     "outputs":[{"name":"Objet","data_type":"any"},{"name":"Erreur","data_type":"string"}],
     "params":[_p("path","Chemin JSONPath","text",""),
               _p("strict","Strict","bool",True)]},
    {"id":"tf_json_build","category":"transform","title":"Créer JSON","icon":"{ + }",
     "description":"Construit un objet JSON.",
     "inputs":[{"name":"Clé 1","data_type":"string"},{"name":"Val 1","data_type":"any"},{"name":"Clé 2","data_type":"string"},{"name":"Val 2","data_type":"any"}],
     "outputs":[{"name":"JSON","data_type":"string"}],
     "params":[_p("indent","Indentation","number",2,min=0,max=8),
               _p("sort_keys","Trier les clés","bool",False)]},
    {"id":"tf_calc",      "category":"transform","title":"Calcul","icon":"∑",
     "description":"Opération arithmétique.",
     "inputs":[{"name":"A","data_type":"number"},{"name":"B","data_type":"number"}],
     "outputs":[{"name":"Résultat","data_type":"number"}],
     "params":[_p("op","Opération","select","+",options=["+","-","×","÷","Modulo","Puissance","Min","Max"]),
               _p("precision","Précision","number",2,min=0,max=15)]},
    {"id":"tf_regex",     "category":"transform","title":"Regex","icon":".*",
     "description":"Extraction par expression régulière.",
     "inputs":[{"name":"Texte","data_type":"string"}],
     "outputs":[{"name":"Match","data_type":"string"},{"name":"Groupes","data_type":"any"},{"name":"Trouvé","data_type":"bool"}],
     "params":[_p("pattern","Pattern","text","(.+)"),
               _p("flags","Flags","select","",options=["","IGNORECASE","MULTILINE","DOTALL"]),
               _p("all_matches","Tous les matches","bool",False)]},
    {"id":"tf_split",     "category":"transform","title":"Découper Texte","icon":"✂",
     "description":"Divise une chaîne en liste.",
     "inputs":[{"name":"Texte","data_type":"string"},{"name":"Séparateur","data_type":"string"}],
     "outputs":[{"name":"Liste","data_type":"any"},{"name":"Nb","data_type":"number"}],
     "params":[_p("sep","Séparateur","text",","),_p("strip","Strip éléments","bool",True),
               _p("limit","Limite (0=∞)","number",0,min=0)]},
    {"id":"tf_replace",   "category":"transform","title":"Remplacer","icon":"⇄",
     "description":"Remplace du texte.",
     "inputs":[{"name":"Texte","data_type":"string"},{"name":"Chercher","data_type":"string"},{"name":"Remplacer","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"string"},{"name":"Nb remplacement","data_type":"number"}],
     "params":[_p("use_regex","Utiliser regex","bool",False),_p("limit","Limite (0=∞)","number",0,min=0)]},
    {"id":"tf_b64",       "category":"transform","title":"Base64","icon":"B64",
     "description":"Encode / décode en Base64.",
     "inputs":[{"name":"Données","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"string"}],
     "params":[_p("mode","Mode","select","Encoder",options=["Encoder","Décoder"]),
               _p("urlsafe","URL-safe","bool",False)]},
    {"id":"tf_hash",      "category":"transform","title":"Hachage","icon":"#",
     "description":"Calcule un hash cryptographique.",
     "inputs":[{"name":"Données","data_type":"string"}],
     "outputs":[{"name":"Hash","data_type":"string"}],
     "params":[_p("algo","Algorithme","select","SHA-256",options=["MD5","SHA-1","SHA-256","SHA-512","BLAKE2"]),
               _p("uppercase","Majuscules","bool",False)]},
    {"id":"tf_date",      "category":"transform","title":"Date / Heure","icon":"📅",
     "description":"Manipule les dates et heures.",
     "inputs":[{"name":"Date","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"string"},{"name":"Timestamp","data_type":"number"}],
     "params":[_p("op","Opération","select","Formater",options=["Formater","Ajouter durée","Différence","Maintenant"]),
               _p("format","Format sortie","text","%Y-%m-%d %H:%M:%S"),
               _p("tz","Fuseau horaire","text","Europe/Paris")]},
    {"id":"tf_template",  "category":"transform","title":"Template Jinja","icon":"🧩",
     "description":"Moteur de template Jinja2.",
     "inputs":[{"name":"Contexte","data_type":"any"}],
     "outputs":[{"name":"Rendu","data_type":"string"}],
     "params":[_p("template","Template","textarea","Bonjour {{ name }} !"),
               _p("strict","Undefined=error","bool",False)]},
    {"id":"tf_csv",       "category":"transform","title":"Parser CSV","icon":"📊",
     "description":"Lit/écrit des données CSV.",
     "inputs":[{"name":"Texte","data_type":"string"}],
     "outputs":[{"name":"Lignes","data_type":"any"},{"name":"Nb","data_type":"number"}],
     "params":[_p("delimiter","Délimiteur","text",","),_p("has_header","En-tête","bool",True),
               _p("quotechar","Guillemets","text",'"')]},
    # ── DATA ──────────────────────────────────────────────────────────────────
    {"id":"data_list",    "category":"data","title":"Liste","icon":"[ ]",
     "description":"Crée ou manipule une liste.",
     "inputs":[{"name":"Item 1","data_type":"any"},{"name":"Item 2","data_type":"any"},{"name":"Item 3","data_type":"any"}],
     "outputs":[{"name":"Liste","data_type":"any"},{"name":"Taille","data_type":"number"}],
     "params":[_p("op","Opération","select","Créer",options=["Créer","Ajouter","Supprimer","Trier","Inverser","Unique"])]},
    {"id":"data_dict",    "category":"data","title":"Dictionnaire","icon":"{ : }",
     "description":"Crée ou manipule un dictionnaire.",
     "inputs":[{"name":"Clé","data_type":"string"},{"name":"Valeur","data_type":"any"},{"name":"Dict","data_type":"any"}],
     "outputs":[{"name":"Dict","data_type":"any"},{"name":"Valeur","data_type":"any"}],
     "params":[_p("op","Opération","select","Créer",options=["Créer","Lire","Mettre à jour","Supprimer","Fusionner","Clés"]),
               _p("key","Clé","text","")]},
    {"id":"data_counter", "category":"data","title":"Compteur","icon":"🔢",
     "description":"Compteur incrémental.",
     "inputs":[{"name":"Incrémenter","type":"exec"},{"name":"Réinitialiser","type":"exec"}],
     "outputs":[{"name":"Valeur","data_type":"number"},{"name":"Exec","type":"exec"}],
     "params":[_p("start","Départ","number",0),_p("step","Pas","number",1),
               _p("max","Max (0=∞)","number",0,min=0)]},
    {"id":"data_cache",   "category":"data","title":"Cache","icon":"💿",
     "description":"Mémoize des valeurs temporairement.",
     "inputs":[{"name":"Écrire","type":"exec"},{"name":"Clé","data_type":"string"},{"name":"Valeur","data_type":"any"}],
     "outputs":[{"name":"Valeur","data_type":"any"},{"name":"Hit","data_type":"bool"}],
     "params":[_p("ttl","TTL (s, 0=∞)","number",300,min=0),
               _p("max_size","Taille max","number",100,min=1)]},
    # ── VARIABLES ─────────────────────────────────────────────────────────────
    {"id":"var_string",   "category":"variable","title":"Variable Texte","icon":"𝑇",
     "description":"Stocke une valeur texte.",
     "inputs":[{"name":"Valeur","data_type":"string"}],
     "outputs":[{"name":"Résultat","data_type":"string"}],
     "params":[_p("name","Nom","text","maVar"),_p("value","Valeur","text",""),
               _p("scope","Portée","select","Locale",options=["Locale","Globale","Persistante"])]},
    {"id":"var_number",   "category":"variable","title":"Variable Nombre","icon":"𝑁",
     "description":"Stocke une valeur numérique.",
     "inputs":[{"name":"Valeur","data_type":"number"}],
     "outputs":[{"name":"Résultat","data_type":"number"}],
     "params":[_p("name","Nom","text","monNb"),_p("value","Valeur","float",0.0,min=-1e9,max=1e9),
               _p("scope","Portée","select","Locale",options=["Locale","Globale","Persistante"])]},
    {"id":"var_bool",     "category":"variable","title":"Variable Bool","icon":"𝐵",
     "description":"Stocke une valeur booléenne.",
     "inputs":[{"name":"Valeur","data_type":"bool"}],
     "outputs":[{"name":"Résultat","data_type":"bool"}],
     "params":[_p("name","Nom","text","monBool"),_p("value","Valeur","bool",False),
               _p("scope","Portée","select","Locale",options=["Locale","Globale","Persistante"])]},
    {"id":"var_const",    "category":"variable","title":"Constante","icon":"π",
     "description":"Valeur immuable.",
     "inputs":[],
     "outputs":[{"name":"Valeur","data_type":"any"}],
     "params":[_p("name","Nom","text","CONSTANTE"),_p("value","Valeur","text","42"),
               _p("type","Type","select","string",options=["string","number","bool","json"])]},
    {"id":"var_env",      "category":"variable","title":"Variable Env","icon":"$",
     "description":"Lit une variable d'environnement.",
     "inputs":[],
     "outputs":[{"name":"Valeur","data_type":"string"},{"name":"Défaut","data_type":"string"}],
     "params":[_p("var_name","Variable","text","HOME"),
               _p("default","Valeur par défaut","text","")]},
    # ── SYSTEM ────────────────────────────────────────────────────────────────
    {"id":"sys_info",     "category":"system","title":"Infos Système","icon":"🖥",
     "description":"Infos sur le système hôte.",
     "inputs":[{"name":"Exec","type":"exec"}],
     "outputs":[{"name":"OS","data_type":"string"},{"name":"CPU %","data_type":"number"},{"name":"RAM %","data_type":"number"},{"name":"Exec","type":"exec"}],
     "params":[_p("interval","Intervalle refresh (s)","number",5,min=1)]},
    {"id":"sys_path",     "category":"system","title":"Opérations Fichier","icon":"🗂",
     "description":"Copie, déplace, supprime des fichiers.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Source","data_type":"string"},{"name":"Dest","data_type":"string"}],
     "outputs":[{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("op","Opération","select","Copier",options=["Copier","Déplacer","Supprimer","Renommer","Créer dossier","Lister dossier"])]},
    {"id":"sys_proc",     "category":"system","title":"Processus","icon":"⚙",
     "description":"Lance ou surveille un processus.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Cmd","data_type":"string"}],
     "outputs":[{"name":"PID","data_type":"number"},{"name":"Stdout","data_type":"string"},{"name":"Succès","type":"exec"}],
     "params":[_p("mode","Mode","select","Démarrer",options=["Démarrer","Arrêter","Statut"]),
               _p("async_mode","Asynchrone","bool",False)]},
    # ── NETWORK ───────────────────────────────────────────────────────────────
    {"id":"net_dns",      "category":"network","title":"DNS Lookup","icon":"🌍",
     "description":"Résout un nom de domaine.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Hôte","data_type":"string"}],
     "outputs":[{"name":"IPs","data_type":"any"},{"name":"Exec","type":"exec"}],
     "params":[_p("record_type","Type","select","A",options=["A","AAAA","MX","TXT","CNAME"]),
               _p("timeout","Timeout (s)","number",5,min=1)]},
    {"id":"net_ping",     "category":"network","title":"Ping","icon":"📡",
     "description":"Teste la connectivité réseau.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Hôte","data_type":"string"}],
     "outputs":[{"name":"Latence ms","data_type":"number"},{"name":"Succès","type":"exec"},{"name":"Échec","type":"exec"}],
     "params":[_p("count","Paquets","number",4,min=1,max=100),
               _p("timeout","Timeout (s)","number",3,min=1)]},
    {"id":"net_ftp",      "category":"network","title":"FTP / SFTP","icon":"📤",
     "description":"Transfert de fichiers FTP/SFTP.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Fichier local","data_type":"string"},{"name":"Dest","data_type":"string"}],
     "outputs":[{"name":"Succès","type":"exec"},{"name":"Erreur","type":"exec"}],
     "params":[_p("protocol","Protocole","select","SFTP",options=["FTP","FTPS","SFTP"]),
               _p("host","Hôte","text",""),_p("port","Port","number",22,min=1,max=65535),
               _p("user","Utilisateur","text",""),
               _p("op","Opération","select","Upload",options=["Upload","Download","Lister"])]},
    {"id":"net_mqtt",     "category":"network","title":"MQTT","icon":"📶",
     "description":"Publie/souscrit à un broker MQTT.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Payload","data_type":"string"}],
     "outputs":[{"name":"Message","data_type":"string"},{"name":"Topic","data_type":"string"}],
     "params":[_p("broker","Broker","text","localhost"),_p("port","Port","number",1883,min=1,max=65535),
               _p("topic","Topic","text","mon/topic"),
               _p("mode","Mode","select","Publier",options=["Publier","Souscrire"])]},
    # ── OUTPUTS ───────────────────────────────────────────────────────────────
    {"id":"out_log",      "category":"output","title":"Journaliser","icon":"📋",
     "description":"Enregistre dans la console.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Message","data_type":"any"}],
     "outputs":[],
     "params":[_p("level","Niveau","select","INFO",options=["INFO","DEBUG","WARNING","ERROR"]),
               _p("prefix","Préfixe","text","[LOG]"),
               _p("to_file","Fichier","bool",False),
               _p("log_path","Chemin log","text","flux.log")]},
    {"id":"out_end",      "category":"output","title":"Terminer","icon":"⬛",
     "description":"Fin du flux.",
     "inputs":[{"name":"Exec","type":"exec"}],
     "outputs":[],
     "params":[_p("exit_code","Code sortie","number",0,min=0,max=255),
               _p("message","Message","text","Flux terminé.")]},
    {"id":"out_ui_dialog","category":"output","title":"Boîte de dialogue","icon":"💬",
     "description":"Affiche une boîte de dialogue.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Message","data_type":"string"}],
     "outputs":[{"name":"OK","type":"exec"},{"name":"Annuler","type":"exec"},{"name":"Réponse","data_type":"string"}],
     "params":[_p("type","Type","select","Information",options=["Information","Avertissement","Erreur","Question","Saisie"]),
               _p("title","Titre","text","Notification"),
               _p("timeout","Auto-fermeture (s)","number",0,min=0)]},
    {"id":"out_webhook",  "category":"output","title":"Appeler Webhook","icon":"📣",
     "description":"Appelle un webhook sortant.",
     "inputs":[{"name":"Exec","type":"exec"},{"name":"Payload","data_type":"string"}],
     "outputs":[{"name":"Succès","type":"exec"},{"name":"Réponse","data_type":"string"}],
     "params":[_p("url","URL","text",""),
               _p("method","Méthode","select","POST",options=["POST","GET","PUT"]),
               _p("format","Format","select","JSON",options=["JSON","Form","Raw"])]},
]

CUSTOM_NODES_FILE = os.path.join(os.path.expanduser("~"), ".tryxee_automations_custom.json")

def load_custom_nodes():
    if os.path.exists(CUSTOM_NODES_FILE):
        try:
            with open(CUSTOM_NODES_FILE) as f:
                return json.load(f)
        except: pass
    return []

def save_custom_nodes(nodes):
    try:
        with open(CUSTOM_NODES_FILE, "w") as f:
            json.dump(nodes, f, ensure_ascii=False, indent=2)
    except: pass

CUSTOM_NODES = load_custom_nodes()
NODE_CATALOG.extend(CUSTOM_NODES)

# ═══════════════════════════════════════════════════════════════════════════════
# PORT ITEM
# ═══════════════════════════════════════════════════════════════════════════════
class PortItem(QGraphicsEllipseItem):
    R = 7
    def __init__(self, node, name, ptype, dtype, idx, is_input, parent=None):
        super().__init__(-self.R,-self.R,self.R*2,self.R*2, parent)
        self.node, self.name = node, name
        self.port_type, self.data_type = ptype, dtype
        self.index, self.is_input = idx, is_input
        self.connections = []
        self._color = self._get_color()
        self._refresh_style()
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
        # Tooltip
        type_str = "exec" if ptype == "exec" else dtype
        self.setToolTip(f"{name}  [{type_str}]")

    def _get_color(self):
        if self.port_type == "exec": return QColor("#e8edf5")
        return {"bool":QColor("#f59e0b"),"number":QColor("#10b981"),
                "string":QColor("#3b82f6"),"any":QColor("#7c3aed")}.get(self.data_type, QColor("#7a8ba0"))

    def _refresh_style(self):
        c = self._color
        self.setPen(QPen(c.darker(130), 1.5))
        self.setBrush(QBrush(T.bg_surface()))

    def hoverEnterEvent(self, e):
        self.setBrush(QBrush(self._color)); self.setScale(1.35); super().hoverEnterEvent(e)
    def hoverLeaveEvent(self, e):
        if not self.connections: self.setBrush(QBrush(T.bg_surface()))
        self.setScale(1.0); super().hoverLeaveEvent(e)
    def mark_connected(self): self.setBrush(QBrush(self._color))
    def scene_pos(self): return self.scenePos()

# ═══════════════════════════════════════════════════════════════════════════════
# CONNECTION ITEM
# ═══════════════════════════════════════════════════════════════════════════════
class ConnectionItem(QGraphicsPathItem):
    def __init__(self, src=None, parent=None):
        super().__init__(parent)
        self.source_port = src
        self.target_port = None
        self.temp_end = QPointF()
        self._anim_t = 0.0
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._color = src._color if src else QColor("#00d4ff")
        self._pen = QPen(self._color, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def update_path(self, end=None):
        if end: self.temp_end = end
        if not self.source_port: return
        s = self.source_port.scene_pos()
        e = self.temp_end if not self.target_port else self.target_port.scene_pos()
        path = QPainterPath(); path.moveTo(s)
        dx = max(abs(e.x()-s.x())*0.6, 60)
        path.cubicTo(s.x()+dx, s.y(), e.x()-dx, e.y(), e.x(), e.y())
        self.setPath(path)

    def paint(self, painter, opt, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        if self.isSelected():
            gp = QPen(QColor(self._color.red(),self._color.green(),self._color.blue(),55), 7, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(gp); painter.drawPath(self.path())
        painter.setPen(self._pen); painter.drawPath(self.path())
        if self.target_port:
            plen = self.path().length()
            if plen > 0:
                pt = self.path().pointAtPercent(self._anim_t % 1.0)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(self._color.lighter(160)))
                painter.drawEllipse(pt, 4, 4)

# ═══════════════════════════════════════════════════════════════════════════════
# NODE ITEM  (expandable)
# ═══════════════════════════════════════════════════════════════════════════════
class NodeItem(QGraphicsItem):
    NODE_W        = 230
    HEADER_H      = 44
    PORT_SPACING  = 26
    PORT_PAD      = 14
    EXPAND_ROW_H  = 28
    CORNER        = 10

    def __init__(self, data, pos=QPointF()):
        super().__init__()
        self.node_data  = data
        self.title      = data["title"]
        self.category   = data["category"]
        self.inputs     = data.get("inputs", [])
        self.outputs    = data.get("outputs", [])
        self._color     = T.cat_color(self.category)
        self.node_id    = data.get("id", str(uuid.uuid4()))
        self.expanded   = False
        self.backend_id = data.get("id") or str(uuid.uuid4())   # id backend / fonction
        self.instance_id = data.get("instance_id") or str(uuid.uuid4())  # id unique du nœud
        self.node_data["id"] = self.backend_id
        self.node_data["instance_id"] = self.instance_id

        # Params storage
        self.node_params = {p["name"]: p.get("default","") for p in data.get("params",[])}

        self.setPos(pos)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(5)
        self._hovered = False

        self._build_ports()
        self._setup_shadow()
        self._update_height()
        
        # assign a stable backend id (use provided id if data contains one)
        self.backend_id = data.get("id") or str(uuid.uuid4())
        # persist back in the node_data so saved files keep it
        self.node_data["id"] = self.backend_id

        # container to hold last computed outputs for this node (filled by runner)
        self.last_outputs = {}

    def _update_height(self):
        n = max(len(self.inputs), len(self.outputs))
        collapsed_h = self.HEADER_H + self.PORT_PAD*2 + n*self.PORT_SPACING + 8
        if self.expanded:
            params = self.node_data.get("params", [])
            self.NODE_H = collapsed_h + len(params)*self.EXPAND_ROW_H + 12
        else:
            self.NODE_H = collapsed_h
        self._reposition_ports()

    def _build_ports(self):
        # build main input/output ports (existing behavior)
        self.input_ports = []
        self.output_ports = []
        self.param_ports = []   # NEW: ports that correspond to params shown when expanded

        for i, pd in enumerate(self.inputs):
            p = PortItem(self, pd["name"], pd.get("type","data"), pd.get("data_type","any"), i, True, self)
            self.input_ports.append(p)
        for i, pd in enumerate(self.outputs):
            p = PortItem(self, pd["name"], pd.get("type","data"), pd.get("data_type","any"), i, False, self)
            self.output_ports.append(p)

        # NEW: create param ports (treated as input ports)
        for i, pd in enumerate(self.node_data.get("params", [])):
            # try to map param "type" to a reasonable data_type for color; fallback to "any"
            ptype = "data"
            dtype = {
                "text": "string", "textarea": "string",
                "number": "number", "float": "number",
                "bool": "bool", "select": "string"
            }.get(pd.get("type", ""), "any")
            p = PortItem(self, pd["name"], ptype, dtype, i, True, self)
            p.setZValue(12)
            self.param_ports.append(p)

        self._reposition_ports()


    def _reposition_ports(self):
        # position side input ports (left edge)
        for i, p in enumerate(self.input_ports):
            y = self.HEADER_H + self.PORT_PAD + i*self.PORT_SPACING + 5
            p.setPos(0, y)
        # position side output ports (right edge)
        for i, p in enumerate(self.output_ports):
            y = self.HEADER_H + self.PORT_PAD + i*self.PORT_SPACING + 5
            p.setPos(self.NODE_W, y)

        # param ports: place them on the LEFT side of the param rows
        if hasattr(self, "param_ports"):
            if self.expanded:
                # compute vertical base (should match paint() layout for param rows)
                base_ports_h = self.HEADER_H + self.PORT_PAD*2 + max(len(self.inputs), len(self.outputs))*self.PORT_SPACING + 8
                for i, p in enumerate(self.param_ports):
                    row_y = base_ports_h + i*self.EXPAND_ROW_H + 6
                    y_center = row_y + (self.EXPAND_ROW_H-4)/2
                    # place the small circle a bit inside from the left border so it appears to the left
                    # of the parameter name/value. Adjust x value if the circle overlaps text in your theme.
                    x = 8
                    p.setVisible(True)
                    p.setPos(x, y_center)
            else:
                for p in self.param_ports:
                    p.setVisible(False)
                    
    def get_param(self, name, default=None):
        """Return a parameter value stored on the node (convenience)."""
        return self.node_params.get(name, default)

    def set_outputs(self, outputs: dict):
        """
        Store outputs computed by the backend function.
        `outputs` should be a dict mapping output-name -> value.
        We store them in self.last_outputs and also mirror them into node.node_params
        under keys prefixed with 'out_' so the UI can read them if you want.
        """
        if not isinstance(outputs, dict):
            return
        self.last_outputs.update(outputs)
        for k, v in outputs.items():
            # optional: mirror into node params for convenience
            self.node_params[f"out_{k}"] = v
        # trigger visual update if your node paint() displays outputs
        try:
            self.update()
        except Exception:
            pass

    def _setup_shadow(self):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(28); sh.setOffset(0, 6)
        sh.setColor(QColor(0,0,0,120))
        self.setGraphicsEffect(sh)

    def toggle_expand(self):
        self.prepareGeometryChange()
        self.expanded = not self.expanded
        self._update_height()
        # reposition ports (including param ports) right after height change
        self._reposition_ports()
        # update existing connection paths for all ports
        for p in self.input_ports + self.output_ports + getattr(self, "param_ports", []):
            for c in p.connections:
                c.update_path()
        self.update()

    def boundingRect(self):
        return QRectF(-2,-2, self.NODE_W+4, self.NODE_H+4)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for p in self.input_ports+self.output_ports:
                for c in p.connections: c.update_path()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, e):
        # Double-click header → toggle expand
        if e.pos().y() < self.HEADER_H:
            self.toggle_expand()
        super().mouseDoubleClickEvent(e)

    def paint(self, painter, opt, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        sel = self.isSelected()
        c   = T.cat_color(self.category)   # live color
        body = QRectF(0, 0, self.NODE_W, self.NODE_H)

        # ─ body ─
        bg0 = T.bg_card(); bg1 = T.bg_surface()
        grad = QLinearGradient(0,0,0,self.NODE_H)
        grad.setColorAt(0, bg0); grad.setColorAt(1, bg1)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(body, self.CORNER, self.CORNER)

        # ─ header ─
        hg = QLinearGradient(0,0,self.NODE_W,0)
        hg.setColorAt(0, QColor(c.red(),c.green(),c.blue(),210))
        hg.setColorAt(1, QColor(c.red()//2,c.green()//2,c.blue()//2,160))
        painter.setBrush(QBrush(hg))
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0,0,self.NODE_W,self.HEADER_H+self.CORNER),self.CORNER,self.CORNER)
        painter.setClipPath(clip); painter.drawRect(QRectF(0,0,self.NODE_W,self.HEADER_H))
        painter.setClipping(False)

        # ─ expand arrow ─
        arrow = "▼" if self.expanded else "▶"
        painter.setPen(QPen(QColor(255,255,255,160)))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(QRectF(self.NODE_W-18, 0, 14, self.HEADER_H), Qt.AlignVCenter|Qt.AlignHCenter, arrow)

        # ─ title + category dot ─
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setBrush(QBrush(QColor(255,255,255,55)))
        painter.setPen(Qt.NoPen); painter.drawEllipse(QRectF(11,14,14,14))
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Segoe UI",9,QFont.Bold))
        painter.drawText(QRectF(30, 0, self.NODE_W-50, self.HEADER_H), Qt.AlignVCenter|Qt.AlignLeft, self.title)

        # ─ variable name badge ─
        if self.category == "variable" and self.node_params.get("name"):
            vname = self.node_params["name"]
            painter.setFont(QFont("Consolas",7))
            painter.setPen(QPen(QColor(255,255,255,180)))
            nr = QRectF(30, self.HEADER_H-14, self.NODE_W-50, 12)
            painter.drawText(nr, Qt.AlignLeft|Qt.AlignVCenter, f"→ {vname}")

        # ─ port labels ─
        painter.setFont(QFont("Segoe UI",8))
        for i, p in enumerate(self.input_ports):
            y = self.HEADER_H + self.PORT_PAD + i*self.PORT_SPACING + 5
            painter.setPen(QPen(T.text_secondary()))
            painter.drawText(QRectF(14,y-8,self.NODE_W//2,16), Qt.AlignVCenter|Qt.AlignLeft, p.name)
        for i, p in enumerate(self.output_ports):
            y = self.HEADER_H + self.PORT_PAD + i*self.PORT_SPACING + 5
            painter.setPen(QPen(T.text_secondary()))
            painter.drawText(QRectF(self.NODE_W//2,y-8,self.NODE_W//2-14,16), Qt.AlignVCenter|Qt.AlignRight, p.name)

        # ─ expanded params section ─
        if self.expanded:
            params = self.node_data.get("params", [])
            base_ports_h = self.HEADER_H + self.PORT_PAD*2 + max(len(self.inputs),len(self.outputs))*self.PORT_SPACING + 8
            # separator
            painter.setPen(QPen(T.border(), 1)); painter.setBrush(Qt.NoBrush)
            painter.drawLine(8, base_ports_h-4, self.NODE_W-8, base_ports_h-4)

            for i, param in enumerate(params):
                row_y = base_ports_h + i*self.EXPAND_ROW_H + 6
                row_r = QRectF(8, row_y, self.NODE_W-16, self.EXPAND_ROW_H-4)
                # row bg
                painter.setPen(Qt.NoPen)
                row_bg = T.bg_surface()
                painter.setBrush(QBrush(row_bg))
                painter.drawRoundedRect(row_r, 4, 4)
                # label
                painter.setFont(QFont("Segoe UI",7,QFont.Bold))
                painter.setPen(QPen(T.text_secondary()))
                painter.drawText(QRectF(row_r.x()+6, row_y, 80, self.EXPAND_ROW_H-4),
                                 Qt.AlignVCenter|Qt.AlignLeft, param["label"])
                # value / binding info
                pname = param["name"]
                # check if connected
                bound_info = self._get_param_binding(pname)
                val_text = bound_info if bound_info else str(self.node_params.get(pname, param.get("default","")))
                val_color = c if bound_info else T.text_primary()
                painter.setFont(QFont("Consolas" if not bound_info else "Segoe UI",7))
                painter.setPen(QPen(val_color))
                painter.drawText(QRectF(row_r.x()+86, row_y, self.NODE_W-110, self.EXPAND_ROW_H-4),
                                 Qt.AlignVCenter|Qt.AlignRight, val_text)

        # ─ border ─
        if sel:
            painter.setPen(QPen(c.lighter(160), 2))
            painter.setBrush(Qt.NoBrush); painter.drawRoundedRect(body, self.CORNER, self.CORNER)
            painter.setPen(QPen(QColor(c.red(),c.green(),c.blue(),45), 8))
            painter.drawRoundedRect(body, self.CORNER, self.CORNER)
        elif self._hovered:
            painter.setPen(QPen(c, 1.5))
            painter.setBrush(Qt.NoBrush); painter.drawRoundedRect(body, self.CORNER, self.CORNER)
        else:
            painter.setPen(QPen(T.border(), 1))
            painter.setBrush(Qt.NoBrush); painter.drawRoundedRect(body, self.CORNER, self.CORNER)

    def _get_param_binding(self, param_name):
        """Return binding label if any input port matches this param name."""
        for p in self.input_ports:
            if p.name.lower() == param_name.lower() and p.connections:
                src = p.connections[0].source_port
                if src: return f"← {src.node.title}"
        return None

    def hoverEnterEvent(self,e): self._hovered=True; self.update(); super().hoverEnterEvent(e)
    def hoverLeaveEvent(self,e): self._hovered=False; self.update(); super().hoverLeaveEvent(e)

    def contextMenuEvent(self, e):
        menu = QMenu(); menu.setStyleSheet(MENU_SS)
        menu.addAction(("▼  Réduire" if self.expanded else "▶  Déployer")).triggered.connect(self.toggle_expand)
        menu.addSeparator()
        menu.addAction("🗑  Supprimer").triggered.connect(self._delete)
        menu.addAction("📋  Dupliquer").triggered.connect(self._duplicate)
        menu.addAction("🎨  Propriétés").triggered.connect(lambda: None)
        menu.exec_(e.screenPos())

    def _delete(self):
        for p in self.input_ports+self.output_ports:
            for c in list(p.connections):
                if c.source_port and c in c.source_port.connections: c.source_port.connections.remove(c)
                if c.target_port and c in c.target_port.connections: c.target_port.connections.remove(c)
                if c.scene(): c.scene().removeItem(c)
        if self.scene(): self.scene().removeItem(self)

    def _duplicate(self):
        if self.scene():
            nn = NodeItem(self.node_data, self.pos()+QPointF(40,40))
            nn.node_params = dict(self.node_params)
            self.scene().addItem(nn)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE
# ═══════════════════════════════════════════════════════════════════════════════
class BlueprintScene(QGraphicsScene):
    node_selected   = pyqtSignal(object)
    node_deselected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000,-5000,10000,10000)
        self._drag_conn = None
        self._drag_src  = None
        self._tick = 0
        t = QTimer(self); t.timeout.connect(self._tick_anim); t.start(30)
        self.selectionChanged.connect(self._on_sel)

    def _on_sel(self):
        sel = [i for i in self.selectedItems() if isinstance(i, NodeItem)]
        if sel: self.node_selected.emit(sel[0])
        else: self.node_deselected.emit()

    def _tick_anim(self):
        self._tick = (self._tick+2)%100
        for it in self.items():
            if isinstance(it, ConnectionItem) and it.target_port:
                it._anim_t = self._tick/100.0; it.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            for it in self.items(e.scenePos()):
                if isinstance(it, PortItem):
                    self._begin_drag(it, e.scenePos()); return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag_conn:
            self._drag_conn.update_path(e.scenePos()); return
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._drag_conn:
            done = False
            for it in self.items(e.scenePos()):
                if isinstance(it, PortItem) and it != self._drag_src:
                    src, tgt = self._drag_src, it
                    if src.is_input and not tgt.is_input: src,tgt = tgt,src
                    if not src.is_input and tgt.is_input and src.node != tgt.node:
                        self._drag_conn.target_port = tgt
                        self._drag_conn.update_path()
                        src.connections.append(self._drag_conn)
                        tgt.connections.append(self._drag_conn)
                        src.mark_connected(); tgt.mark_connected()
                        tgt.node.update()   # refresh binding display
                        done = True; break
            if not done: self.removeItem(self._drag_conn)
            self._drag_conn = self._drag_src = None; return
        super().mouseReleaseEvent(e)

    def _begin_drag(self, port, pos):
        c = ConnectionItem(port)
        c.temp_end = pos; c.update_path()
        self.addItem(c)
        self._drag_conn = c; self._drag_src = port

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QBrush(T.bg_deep()))
        self._grid(painter, rect)

    def _grid(self, painter, r):
        for size, col in [(20, T.bg_surface()), (100, T.bg_panel())]:
            pen = QPen(col, 1); painter.setPen(pen)
            x0 = int(r.left())-(int(r.left())%size)
            y0 = int(r.top())-(int(r.top())%size)
            for x in range(x0, int(r.right()), size):
                painter.drawLine(x,int(r.top()),x,int(r.bottom()))
            for y in range(y0, int(r.bottom()), size):
                painter.drawLine(int(r.left()),y,int(r.right()),y)
        painter.setPen(QPen(T.border(), 1))
        painter.drawLine(-5000,0,5000,0); painter.drawLine(0,-5000,0,5000)

# ═══════════════════════════════════════════════════════════════════════════════
# VIEW
# ═══════════════════════════════════════════════════════════════════════════════
class BlueprintView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform|QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        for sb in (self.horizontalScrollBar(), self.verticalScrollBar()):
            sb.setStyleSheet("QScrollBar{width:0;height:0}")
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFrameShape(QFrame.NoFrame)
        self._pan=False; self._pan0=None; self._zoom=1.0

    def wheelEvent(self, e):
        f = 1.15 if e.angleDelta().y()>0 else 1/1.15
        nz = self._zoom*f
        if 0.15 <= nz <= 4.0:
            self._zoom=nz; self.scale(f,f)

    def mousePressEvent(self, e):
        if e.button()==Qt.MiddleButton or (e.button()==Qt.LeftButton and e.modifiers()==Qt.AltModifier):
            self._pan=True; self._pan0=e.pos(); self.setCursor(Qt.ClosedHandCursor)
        elif e.button()==Qt.RightButton and not self.itemAt(e.pos()):
            self._pan=True; self._pan0=e.pos(); self.setCursor(Qt.ClosedHandCursor); return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._pan and self._pan0:
            d=e.pos()-self._pan0; self._pan0=e.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-d.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-d.y())
        else: super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._pan: self._pan=False; self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            for it in self.scene().selectedItems():
                if isinstance(it, NodeItem): it._delete()
                elif isinstance(it, ConnectionItem):
                    for p in (it.source_port, it.target_port):
                        if p and it in p.connections: p.connections.remove(it)
                    self.scene().removeItem(it)
        elif e.key()==Qt.Key_F: self.fit_all()
        super().keyPressEvent(e)

    def fit_all(self):
        nodes=[i for i in self.scene().items() if isinstance(i,NodeItem)]
        if nodes:
            r=reduce(lambda a,b:a.united(b),[i.mapToScene(i.boundingRect()).boundingRect() for i in nodes])
            self.fitInView(r.adjusted(-60,-60,60,60), Qt.KeepAspectRatio)

# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTIES PANEL
# ═══════════════════════════════════════════════════════════════════════════════
class PropertiesPanel(QWidget):
    W = 300
    node_focus_requested = pyqtSignal(object)  # emits NodeItem to focus in view

    def __init__(self):
        super().__init__()
        self.setMaximumWidth(0); self.setMinimumWidth(0)
        self._node = None; self._widgets = {}
        self._build_ui()
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(250); self._anim.setEasingCurve(QEasingCurve.OutCubic)
        TM.changed.connect(self._refresh_theme)

    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # header
        self.hdr = QWidget(); self.hdr.setFixedHeight(52)
        hl = QHBoxLayout(self.hdr); hl.setContentsMargins(14,0,10,0); hl.setSpacing(8)
        self.dot = QLabel("●"); self.dot.setFixedSize(10,10)
        self.title_l = QLabel("Propriétés")
        self.title_l.setFont(QFont("Segoe UI",10,QFont.Bold))
        x_btn = QPushButton("✕"); x_btn.setFixedSize(24,24)
        x_btn.setCursor(Qt.PointingHandCursor); x_btn.clicked.connect(self.close_panel)
        hl.addWidget(self.dot); hl.addWidget(self.title_l)
        hl.addStretch(); hl.addWidget(x_btn)
        root.addWidget(self.hdr)

        self.accent = QFrame(); self.accent.setFixedHeight(2); root.addWidget(self.accent)

        # description
        self.desc_w = QWidget()
        dl = QVBoxLayout(self.desc_w); dl.setContentsMargins(14,10,14,10)
        self.desc_l = QLabel(); self.desc_l.setWordWrap(True)
        self.desc_l.setFont(QFont("Segoe UI",8))
        dl.addWidget(self.desc_l); root.addWidget(self.desc_w)

        # scroll area
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pcon = QWidget()
        self.play = QVBoxLayout(self.pcon); self.play.setContentsMargins(12,12,12,12)
        self.play.setSpacing(8); self.play.addStretch()
        scroll.setWidget(self.pcon); root.addWidget(scroll)

        # bottom bar
        bot = QWidget(); bot.setFixedHeight(52)
        bl = QHBoxLayout(bot); bl.setContentsMargins(12,0,12,0); bl.setSpacing(8)
        rst = QPushButton("↺  Reset"); rst.setFixedHeight(32); rst.setCursor(Qt.PointingHandCursor)
        rst.clicked.connect(self._reset)
        apl = QPushButton("✓  Appliquer"); apl.setFixedHeight(32)
        apl.setObjectName("apply_btn"); apl.setCursor(Qt.PointingHandCursor)
        apl.clicked.connect(self._apply)
        bl.addWidget(rst); bl.addStretch(); bl.addWidget(apl)
        root.addWidget(bot)
        self._bot = bot; self._rst = rst; self._apl = apl
        self._refresh_theme()

    def _refresh_theme(self):
        bd = T.bg_deep().name(); bp = T.bg_panel().name(); bc = T.bg_card().name()
        bor= T.border().name(); tp = T.text_primary().name(); ts = T.text_secondary().name()
        ac = T.accent().name()
        self.setStyleSheet(f"QWidget{{background:{bp};border:none;}}")
        self.hdr.setStyleSheet(f"background:{bc};")
        self.dot.setStyleSheet("border-radius:5px;")
        self.title_l.setStyleSheet(f"color:{tp};")
        self.desc_w.setStyleSheet(f"QWidget{{background:{T.bg_surface().name()};border-bottom:1px solid {bor};}}")
        self.desc_l.setStyleSheet(f"color:{ts};background:transparent;")
        self._bot.setStyleSheet(f"QWidget{{background:{bc};border-top:1px solid {bor};}}")
        self._rst.setStyleSheet(f"""QPushButton{{background:transparent;border:1px solid {bor};
            border-radius:6px;color:{ts};padding:0 12px;}}
            QPushButton:hover{{background:{bor};color:white;}}""")
        self._apl.setStyleSheet(f"""QPushButton{{background:rgba(0,212,255,12);border:1px solid {ac};
            border-radius:6px;color:{ac};padding:0 16px;}}
            QPushButton:hover{{background:{ac};color:#0a0c10;}}""")

    def show_node(self, node):
        self._node = node
        self._populate(node)
        self._open()

    def close_panel(self): self._close()

    def _open(self):
        self._anim.stop()
        self._anim.setStartValue(self.maximumWidth() if self.maximumWidth()<9999 else 0)
        self._anim.setEndValue(self.W); self._anim.start()

    def _close(self):
        self._anim.stop()
        self._anim.setStartValue(self.maximumWidth() if self.maximumWidth()<9999 else self.W)
        self._anim.setEndValue(0); self._anim.start()

    def _populate(self, node):
        # header visuals
        c = T.cat_color(node.category)
        self.dot.setStyleSheet(f"background:{c.name()};border-radius:5px;")
        self.accent.setStyleSheet(f"background:{c.name()};")
        self.hdr.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 rgba({c.red()},{c.green()},{c.blue()},35),"
            f"stop:1 {T.bg_card().name()});")
        self.title_l.setText(node.title)
        self.desc_l.setText(node.node_data.get("description",""))

        # clear previous widgets
        self._node = node
        self._widgets = {}
        while self.play.count()>1:
            it = self.play.takeAt(0)
            if it.widget(): it.widget().deleteLater()

        # PARAMÈTRES
        params = node.node_data.get("params", [])
        sec_params = QLabel("PARAMÈTRES")
        sec_params.setFont(QFont("Segoe UI",7,QFont.Bold))
        sec_params.setStyleSheet(f"color:{c.name()};letter-spacing:1.5px;padding-bottom:4px;")
        self.play.insertWidget(0, sec_params)

        if not params:
            lbl = QLabel("Aucun paramètre configurable.")
            lbl.setAlignment(Qt.AlignCenter); lbl.setFont(QFont("Segoe UI",8))
            lbl.setStyleSheet(f"color:{T.text_dim().name()};")
            self.play.insertWidget(1, lbl)
        else:
            for i, param in enumerate(params):
                w = self._make_field(param, node, c)
                self.play.insertWidget(i+1, w)

        # --- INPUTS section (nouveau) ---
        inputs_widget = self._build_inputs_section(node, c)
        self.play.insertWidget(self.play.count()-1, inputs_widget)

        # keep bottom stretch
        
    
            
    def _make_id_field(self, node):
        wrap = QWidget()
        ly = QHBoxLayout(wrap); ly.setContentsMargins(6,6,6,6)
        lbl = QLabel("ID")
        lbl.setFixedWidth(28)
        edit = QLineEdit()
        edit.setText(getattr(node, "backend_id", ""))
        edit.setToolTip("Identifiant backend du bloc — utilisé pour lier une fonction dans functions.py")
        def _on_edit_finished():
            new_id = edit.text().strip()
            if not new_id:
                # do nothing / revert (or generate new)
                edit.setText(node.backend_id)
                return
            # update node backend id
            node.backend_id = new_id
            node.node_data["id"] = new_id
            node.update()
        edit.editingFinished.connect(_on_edit_finished)
        ly.addWidget(lbl); ly.addWidget(edit)
        return wrap

    def _make_field(self, param, node, accent_color):
        """
        Field builder for PropertiesPanel.
        - param: dict with 'name','label','type', possibly 'options','min','max','step','default'
        - node: NodeItem instance
        """
        pn = param["name"]
        pl = param.get("label", pn)
        ptype = param.get("type", "text")
        cur = node.node_params.get(pn, param.get("default", ""))

        wrap = QWidget()
        wrap.setObjectName("field_wrap")
        ly = QVBoxLayout(wrap); ly.setContentsMargins(6,6,6,6); ly.setSpacing(4)

        # top label
        top = QWidget(); tlh = QHBoxLayout(top); tlh.setContentsMargins(0,0,0,0)
        lbl = QLabel(pl)
        lbl.setFont(QFont("Segoe UI",9))
        tlh.addWidget(lbl)
        tlh.addStretch()
        ly.addWidget(top)

        # middle: editor widget + binding info on the right
        row = QWidget(); rlay = QHBoxLayout(row); rlay.setContentsMargins(0,0,0,0); rlay.setSpacing(8)

        # ----- editor depending on type -----
        editor = None
        if ptype in ("text",):
            editor = QLineEdit()
            editor.setText(str(cur))
            def _on_edit_finished(e=editor, node=node, pn=pn):
                val = e.text()
                node.node_params[pn] = val
                node.update()
            editor.editingFinished.connect(_on_edit_finished)

        elif ptype in ("textarea",):
            editor = QTextEdit()
            editor.setPlainText(str(cur))
            editor.setFixedHeight(72)
            def _on_text_change(e=editor, node=node, pn=pn):
                val = e.toPlainText()
                node.node_params[pn] = val
                node.update()
            editor.textChanged.connect(lambda e=editor: _on_text_change(e))

        elif ptype in ("number","float","int"):
            # use float spinbox for generality
            editor = QDoubleSpinBox()
            editor.setMinimum(float(param.get("min", -1e9)))
            editor.setMaximum(float(param.get("max", 1e9)))
            editor.setSingleStep(float(param.get("step", 1.0)))
            try:
                editor.setValue(float(cur))
            except Exception:
                editor.setValue(0.0)
            def _on_val_change(v, node=node, pn=pn):
                node.node_params[pn] = v
                node.update()
            editor.valueChanged.connect(_on_val_change)

        elif ptype in ("bool","checkbox"):
            editor = QCheckBox()
            editor.setChecked(bool(cur))
            def _on_state_change(s, node=node, pn=pn):
                node.node_params[pn] = bool(s)
                node.update()
            editor.stateChanged.connect(_on_state_change)

        elif ptype in ("select",):
            editor = QComboBox()
            opts = param.get("options", [])
            for o in opts:
                editor.addItem(str(o), o)
            if cur in opts:
                editor.setCurrentIndex(opts.index(cur))
            def _on_sel(idx, ed=editor, node=node, pn=pn):
                val = ed.itemData(idx)
                node.node_params[pn] = val
                node.update()
            editor.currentIndexChanged.connect(_on_sel)

        else:
            # fallback to single-line editor
            editor = QLineEdit()
            editor.setText(str(cur))
            def _on_edit_finished(e=editor, node=node, pn=pn):
                val = e.text()
                node.node_params[pn] = val
                node.update()
            editor.editingFinished.connect(_on_edit_finished)

        editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        rlay.addWidget(editor)

        # ----- binding indicator (now clickable) and clear button -----
        # find corresponding input param port on the node (param_ports + input_ports)
        tgt_port = None
        for p in node.input_ports + getattr(node, "param_ports", []):
            if p.name.lower() == pn.lower():
                tgt_port = p
                break

        bind_widget = QWidget(); b_ly = QHBoxLayout(bind_widget); b_ly.setContentsMargins(0,0,0,0)
        b_ly.setSpacing(6)

        # clickable button (flat) that shows source node and optionally a short readonly preview of its value
        bind_btn = QPushButton()
        bind_btn.setFlat(True)
        bind_btn.setCursor(Qt.PointingHandCursor)
        bind_btn.setStyleSheet("QPushButton{border: none; text-align: left;}")  # looks like a link
        bind_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # small helper to read a sensible value from a candidate source node (best-effort)
        def _read_node_value(n):
            # common patterns: node.node_params['value'] or 'val' or 'default'
            if not n: return None
            try:
                # try common keys
                for key in ("value","val","default","initial"):
                    if hasattr(n, "node_params") and key in n.node_params:
                        return n.node_params[key]
                # try attributes
                for attr in ("value","val","_value"):
                    if hasattr(n, attr):
                        return getattr(n, attr)
                # fallback: if node.node_params has a single key, show it
                if hasattr(n, "node_params") and isinstance(n.node_params, dict) and len(n.node_params)==1:
                    return next(iter(n.node_params.values()))
            except Exception:
                pass
            return None

        # helper to create a short preview string
        def _preview_text(v, maxlen=30):
            if v is None: return ""
            s = str(v)
            if len(s) > maxlen:
                return s[:maxlen-1] + "…"
            return s

        def refresh_binding_label():
            # default state (no binding)
            bind_btn.setText("") 
            bind_btn.setToolTip("")
            bind_btn.setEnabled(False)

            if tgt_port and tgt_port.connections:
                src = tgt_port.connections[0].source_port
                if src and src.node:
                    src_node = src.node
                    # preview value (best-effort)
                    val = _read_node_value(src_node)
                    preview = _preview_text(val)
                    # show "← NodeTitle (preview)" if preview is short and primitive; tooltip always shows full value
                    if preview:
                        bind_btn.setText(f"← {src_node.title} ({preview})")
                    else:
                        bind_btn.setText(f"← {src_node.title}")
                    # tooltip with full value if any
                    if val is not None:
                        bind_btn.setToolTip(f"Valeur : {str(val)}\nClique pour centrer sur le nœud")
                    else:
                        bind_btn.setToolTip(f"Clique pour centrer sur le nœud")
                    bind_btn.setEnabled(True)
                    return
            # else: no binding
            bind_btn.setText("")
            bind_btn.setToolTip("")
            bind_btn.setEnabled(False)

        # clicking focuses / selects the source node in the view
        def _on_bind_clicked():
            if not tgt_port or not tgt_port.connections:
                return
            src = tgt_port.connections[0].source_port
            if not src or not src.node:
                return
            src_node = src.node
            sc = src_node.scene()
            if not sc:
                return
            # try to find a view showing the scene
            views = sc.views()
            view = views[0] if views else None
            # center the view on the node and give it focus, also select the node
            try:
                if view is not None:
                    # centerOn accepts QGraphicsItem
                    view.centerOn(src_node)
                    view.setFocus()
            except Exception:
                pass
            # select/flash the node (best-effort)
            try:
                # many NodeItem implementations support setSelected(True)
                src_node.setSelected(True)
            except Exception:
                pass
            # update tooltip (value may have changed)
            refresh_binding_label()

        bind_btn.clicked.connect(_on_bind_clicked)

        # clear button (same behavior as before)
        clear_btn = QPushButton("Effacer")
        clear_btn.setFixedSize(60,20)

        def _clear_binding():
            if not tgt_port or not tgt_port.connections:
                refresh_binding_label(); return
            old_conn = tgt_port.connections[0]
            if old_conn.source_port and old_conn in old_conn.source_port.connections:
                old_conn.source_port.connections.remove(old_conn)
            if old_conn.target_port and old_conn in old_conn.target_port.connections:
                old_conn.target_port.connections.remove(old_conn)
            if old_conn.scene():
                old_conn.scene().removeItem(old_conn)
            refresh_binding_label()
            # reset editor to stored param value
            if isinstance(editor, QLineEdit):
                val = node.node_params.get(pn, param.get("default",""))
                editor.setText(str(val))
            elif isinstance(editor, QTextEdit):
                val = node.node_params.get(pn, param.get("default",""))
                editor.setPlainText(str(val))
            elif isinstance(editor, QCheckBox):
                editor.setChecked(bool(node.node_params.get(pn, param.get("default", False))))
            elif isinstance(editor, QComboBox):
                val = node.node_params.get(pn, param.get("default",""))
                try:
                    idx = param.get("options", []).index(val)
                    editor.setCurrentIndex(idx)
                except Exception:
                    pass
            node.update()

        clear_btn.clicked.connect(_clear_binding)

        b_ly.addWidget(bind_btn)
        b_ly.addWidget(clear_btn)
        rlay.addWidget(bind_widget)

        ly.addWidget(row)

        # initial update of binding label state
        refresh_binding_label()

        # IMPORTANT: expose refresh function so external code can call it if bindings change
        # (useful when connections are created/deleted elsewhere)
        wrap.refresh_binding_label = refresh_binding_label

        return wrap

        # handle changes
        def _on_cb_change(idx, cb=cb, node=node, pn=pn, val_lbl=val_lbl):
            sel = cb.itemData(idx)
            # remove previous binding (if any)
            if tgt_port and tgt_port.connections:
                old_conn = tgt_port.connections[0]
                # detach from ports
                if old_conn.source_port and old_conn in old_conn.source_port.connections:
                    old_conn.source_port.connections.remove(old_conn)
                if old_conn.target_port and old_conn in old_conn.target_port.connections:
                    old_conn.target_port.connections.remove(old_conn)
                # remove from scene
                if old_conn.scene(): old_conn.scene().removeItem(old_conn)
                # refresh visuals
                if tgt_port: tgt_port.node.update()

            if sel is None:
                # none selected
                val_lbl.setText(str(node.node_params.get(pn, param.get("default",""))))
                node.update()
                return

            # sel is a PortItem (source)
            src_port = sel
            # find target input port again (safe)
            tport = None
            for p in node.input_ports:
                if p.name.lower() == pn.lower():
                    tport = p; break
            if not tport:
                # nothing to bind to
                val_lbl.setText("Aucun port cible")
                return

            # create new ConnectionItem and attach
            conn = ConnectionItem(src_port)
            conn.target_port = tport
            conn.update_path()
            sc = node.scene()
            if sc:
                sc.addItem(conn)
            src_port.connections.append(conn)
            tport.connections.append(conn)
            src_port.mark_connected(); tport.mark_connected()
            node.update()
            # update displayed label
            val_lbl.setText(f"← {src_port.node.title}")

        cb.currentIndexChanged.connect(_on_cb_change)

        rlay.addWidget(cb)
        ly.addWidget(row)

        return wrap

    def _build_inputs_section(self, node, accent_color):
        """
        Construis la section Inputs (input_ports + param_ports).
        Affiche :
        - si connecté : bouton readonly "← Source (preview)" + bouton Dégager
        - si non connecté : champ éditable qui écrit dans node.node_params[port.name]
        """
        wrap = QWidget()
        vlay = QVBoxLayout(wrap); vlay.setContentsMargins(8,6,8,6); vlay.setSpacing(6)

        hdr = QLabel("INPUTS")
        hdr.setFont(QFont("Segoe UI",7,QFont.Bold))
        hdr.setStyleSheet(f"color:{accent_color.name()};letter-spacing:1.5px;padding-bottom:4px;")
        vlay.addWidget(hdr)

        # collect ports
        ports = list(getattr(node, "input_ports", [])) + list(getattr(node, "param_ports", []))

        # container for refresh callbacks (when binding changes)
        callbacks = []
        wrap._refresh_callbacks = callbacks

        for p in ports:
            row = QWidget(); rlay = QHBoxLayout(row); rlay.setContentsMargins(0,0,0,0); rlay.setSpacing(8)
            lbl = QLabel(p.name); lbl.setFont(QFont("Segoe UI",9)); lbl.setFixedWidth(130)
            rlay.addWidget(lbl)

            # find connection (first)
            conn = None
            if getattr(p, "connections", None):
                if len(p.connections) > 0:
                    conn = p.connections[0]

            if conn and getattr(conn, "source_port", None):
                src_port = conn.source_port
                src_node = getattr(src_port, "node", None)

                # preview value best-effort
                preview_val = None
                try:
                    if getattr(src_node, "last_outputs", None):
                        preview_val = src_node.last_outputs.get(src_port.name)
                    if preview_val is None and hasattr(src_node, "node_params"):
                        preview_val = src_node.node_params.get(src_port.name) or src_node.node_params.get("value")
                except Exception:
                    preview_val = None

                preview_str = ""
                if preview_val is not None:
                    s = str(preview_val)
                    preview_str = s if len(s) < 40 else (s[:37] + "…")

                btn = QPushButton(f"← {getattr(src_node,'title', 'node')}" + (f" ({preview_str})" if preview_str else ""))
                btn.setFlat(True); btn.setCursor(Qt.PointingHandCursor); btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                btn.setToolTip(f"Source: {getattr(src_node,'title',None)}\nValeur: {str(preview_val)}\nClique pour centrer")
                def _center(src_node=src_node):
                    try:
                        sc = src_node.scene()
                        if sc and sc.views():
                            v = sc.views()[0]
                            v.centerOn(src_node); v.setFocus()
                            src_node.setSelected(True)
                    except Exception:
                        pass
                btn.clicked.connect(_center)
                rlay.addWidget(btn)

                clear_btn = QPushButton("Dégager"); clear_btn.setFixedSize(80,22)
                def _clear(conn=conn, tgt_port=p):
                    try:
                        if conn in conn.source_port.connections:
                            conn.source_port.connections.remove(conn)
                        if conn in conn.target_port.connections:
                            conn.target_port.connections.remove(conn)
                        if conn.scene():
                            conn.scene().removeItem(conn)
                    except Exception:
                        pass
                    # refresh panel
                    try:
                        self._populate(node)
                    except Exception:
                        pass
                clear_btn.clicked.connect(_clear)
                rlay.addWidget(clear_btn)

            else:
                # NOT connected -> editable field (fallback to node.node_params)
                cur = node.node_params.get(p.name, "")
                editor = QLineEdit()
                editor.setText("" if cur is None else str(cur))
                editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                def _on_edit(e=editor, node=node, pname=p.name):
                    node.node_params[pname] = e.text()
                    node.update()
                editor.editingFinished.connect(_on_edit)
                rlay.addWidget(editor)

                # register refresh callback so clearing a connection can update editor
                def _refresh_editor(ed=editor, node=node, pname=p.name):
                    try:
                        val = node.node_params.get(pname, "")
                        if isinstance(ed, QLineEdit):
                            ed.setText("" if val is None else str(val))
                    except Exception:
                        pass
                callbacks.append(_refresh_editor)

            vlay.addWidget(row)

        # attach refresh helper
        def _refresh_all():
            for cb in getattr(wrap, "_refresh_callbacks", []):
                try: cb()
                except Exception: pass
        wrap.refresh_all = _refresh_all

        return wrap
    
    def _bind_param_to_port(self, node, param_name, src_port):
        """
        Utility (optional): directly bind a param to a given src_port programmatically.
        Creates a ConnectionItem between src_port and the node's input port matching param_name.
        """
        # find target port
        tport = None
        for p in node.input_ports:
            if p.name.lower() == param_name.lower():
                tport = p; break
        if not tport or src_port is None or src_port.node is node:
            return False
        # remove existing
        if tport.connections:
            old = tport.connections[0]
            if old.source_port and old in old.source_port.connections:
                old.source_port.connections.remove(old)
            if old.target_port and old in old.target_port.connections:
                old.target_port.connections.remove(old)
            if old.scene(): old.scene().removeItem(old)
        # create
        c = ConnectionItem(src_port); c.target_port = tport; c.update_path()
        if node.scene(): node.scene().addItem(c)
        src_port.connections.append(c); tport.connections.append(c)
        src_port.mark_connected(); tport.mark_connected()
        node.update()
        return True

    def _find_source_node(self, node, param_name):
        for p in node.input_ports:
            if p.name.lower()==param_name.lower() and p.connections:
                return p.connections[0].source_port.node if p.connections[0].source_port else None
        return None

    def _read_values(self):
        vals = {}
        for k,w in self._widgets.items():
            if w is None: continue
            if isinstance(w, QLineEdit): vals[k]=w.text()
            elif isinstance(w, QTextEdit): vals[k]=w.toPlainText()
            elif isinstance(w, (QSpinBox,QDoubleSpinBox)): vals[k]=w.value()
            elif isinstance(w, QCheckBox): vals[k]=w.isChecked()
            elif isinstance(w, QComboBox): vals[k]=w.currentText()
        return vals

    def _apply(self):
        if not self._node: return
        self._node.node_params.update(self._read_values())
        self._node.update()

    def _reset(self):
        if not self._node: return
        for p in self._node.node_data.get("params",[]):
            self._node.node_params[p["name"]] = p.get("default","")
        self._populate(self._node)

    def refresh_for_node(self, node):
        """Refresh panel if showing this node (e.g. after a connection)."""
        if self._node is node: self._populate(node)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM NODE DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class CustomNodeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer un nœud personnalisé")
        self.setMinimumSize(600, 620)
        self.setStyleSheet(f"""QDialog{{background:{T.bg_panel().name()};}}
            QLabel{{color:{T.text_primary().name()};background:transparent;}}
            QLineEdit,QTextEdit,QComboBox,QSpinBox{{background:{T.bg_card().name()};
              border:1px solid {T.border().name()};border-radius:5px;
              color:{T.text_primary().name()};padding:4px 8px;font-size:10px;}}
            QLineEdit:focus,QTextEdit:focus,QComboBox:focus{{border-color:{T.accent().name()};}}
            QGroupBox{{color:{T.text_secondary().name()};border:1px solid {T.border().name()};
              border-radius:6px;margin-top:10px;padding-top:8px;font-size:9px;}}
            QPushButton{{background:{T.bg_card().name()};border:1px solid {T.border().name()};
              border-radius:5px;color:{T.text_primary().name()};padding:5px 14px;}}
            QPushButton:hover{{background:{T.border().name()};}}""")
        self._ports_in = []   # list of (name_edit, dtype_combo)
        self._ports_out= []
        self._params   = []   # list of (name,label,type,default) edits
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setSpacing(10); lay.setContentsMargins(16,16,16,16)

        # basic info
        info_g = QGroupBox("Informations générales"); lay.addWidget(info_g)
        fl = QFormLayout(info_g); fl.setSpacing(8)
        self.name_e = QLineEdit("MonNœud"); self.name_e.setFixedHeight(30)
        self.cat_e = QComboBox()
        cats = ["trigger","condition","action","transform","data","flow","variable","system","network","output","custom"]
        [self.cat_e.addItem(c) for c in cats]; self.cat_e.setCurrentText("custom")
        self.cat_e.setFixedHeight(30)
        self.icon_e = QLineEdit("⚙"); self.icon_e.setFixedHeight(30)
        self.desc_e = QLineEdit("Description du nœud"); self.desc_e.setFixedHeight(30)
        fl.addRow("Nom :", self.name_e); fl.addRow("Catégorie :", self.cat_e)
        fl.addRow("Icône :", self.icon_e); fl.addRow("Description :", self.desc_e)

        # ports
        ports_g = QGroupBox("Ports"); lay.addWidget(ports_g)
        pg = QHBoxLayout(ports_g); pg.setSpacing(12)
        # inputs
        in_frame = QWidget(); in_lay = QVBoxLayout(in_frame); in_lay.setContentsMargins(0,0,0,0); in_lay.setSpacing(4)
        in_lay.addWidget(self._sec_lbl("Entrées"))
        self.in_list = QWidget(); self.in_list_lay = QVBoxLayout(self.in_list)
        self.in_list_lay.setContentsMargins(0,0,0,0); self.in_list_lay.setSpacing(4)
        in_lay.addWidget(self.in_list)
        add_in = QPushButton("+ Entrée"); add_in.setFixedHeight(26)
        add_in.clicked.connect(lambda: self._add_port(True))
        in_lay.addWidget(add_in); pg.addWidget(in_frame)
        # outputs
        out_frame = QWidget(); out_lay = QVBoxLayout(out_frame); out_lay.setContentsMargins(0,0,0,0); out_lay.setSpacing(4)
        out_lay.addWidget(self._sec_lbl("Sorties"))
        self.out_list = QWidget(); self.out_list_lay = QVBoxLayout(self.out_list)
        self.out_list_lay.setContentsMargins(0,0,0,0); self.out_list_lay.setSpacing(4)
        out_lay.addWidget(self.out_list)
        add_out = QPushButton("+ Sortie"); add_out.setFixedHeight(26)
        add_out.clicked.connect(lambda: self._add_port(False))
        out_lay.addWidget(add_out); pg.addWidget(out_frame)

        # params
        param_g = QGroupBox("Paramètres"); lay.addWidget(param_g)
        par_v = QVBoxLayout(param_g); par_v.setSpacing(4)
        self.param_list = QWidget(); self.param_list_lay = QVBoxLayout(self.param_list)
        self.param_list_lay.setContentsMargins(0,0,0,0); self.param_list_lay.setSpacing(4)
        par_v.addWidget(self.param_list)
        add_par = QPushButton("+ Paramètre"); add_par.setFixedHeight(26)
        add_par.clicked.connect(self._add_param); par_v.addWidget(add_par)

        # script
        script_g = QGroupBox("Script Python (exécuté lors du Run)"); lay.addWidget(script_g)
        sv = QVBoxLayout(script_g)
        self.script_e = QTextEdit()
        self.script_e.setPlainText("# Paramètres disponibles dans: params dict\n# Inputs disponibles dans: inputs dict\ndef run(params, inputs):\n    # votre code ici\n    return {}")
        self.script_e.setFont(QFont("Consolas",9)); self.script_e.setFixedHeight(120)
        sv.addWidget(self.script_e)

        # buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Créer le nœud")
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        # default ports
        self._add_port(True, "Exec", "exec"); self._add_port(False, "Exec", "exec")

    def _sec_lbl(self, t):
        l = QLabel(t); l.setFont(QFont("Segoe UI",8,QFont.Bold))
        l.setStyleSheet(f"color:{T.accent().name()};"); return l

    def _add_port(self, is_input, default_name="Port", default_type="any"):
        row = QWidget(); row_l = QHBoxLayout(row); row_l.setContentsMargins(0,0,0,0); row_l.setSpacing(4)
        ne = QLineEdit(default_name); ne.setFixedHeight(24); ne.setPlaceholderText("Nom")
        tc = QComboBox(); [tc.addItem(t) for t in ["exec","any","string","number","bool"]]
        tc.setCurrentText(default_type); tc.setFixedHeight(24); tc.setFixedWidth(80)
        rm = QPushButton("✕"); rm.setFixedSize(22,22)
        rm.setStyleSheet(f"QPushButton{{background:transparent;border:none;color:{T.danger().name()};}}QPushButton:hover{{color:white;}}")
        if is_input:
            entry=(ne,tc); self._ports_in.append(entry)
            rm.clicked.connect(lambda _,e=entry,r=row,l=self.in_list_lay: self._remove_port(e,r,l,self._ports_in))
            row_l.addWidget(ne); row_l.addWidget(tc); row_l.addWidget(rm)
            self.in_list_lay.addWidget(row)
        else:
            entry=(ne,tc); self._ports_out.append(entry)
            rm.clicked.connect(lambda _,e=entry,r=row,l=self.out_list_lay: self._remove_port(e,r,l,self._ports_out))
            row_l.addWidget(ne); row_l.addWidget(tc); row_l.addWidget(rm)
            self.out_list_lay.addWidget(row)

    def _remove_port(self, entry, row, layout, lst):
        if entry in lst: lst.remove(entry)
        layout.removeWidget(row); row.deleteLater()

    def _add_param(self):
        row = QWidget(); row_l = QHBoxLayout(row); row_l.setContentsMargins(0,0,0,0); row_l.setSpacing(4)
        ne = QLineEdit("param"); ne.setFixedHeight(24); ne.setPlaceholderText("Nom interne")
        le = QLineEdit("Label"); le.setFixedHeight(24); le.setPlaceholderText("Label")
        tc = QComboBox(); [tc.addItem(t) for t in ["text","number","float","bool","select","textarea"]]
        tc.setFixedHeight(24); tc.setFixedWidth(75)
        de = QLineEdit(""); de.setFixedHeight(24); de.setPlaceholderText("Défaut")
        rm = QPushButton("✕"); rm.setFixedSize(22,22)
        rm.setStyleSheet(f"QPushButton{{background:transparent;border:none;color:{T.danger().name()};}}QPushButton:hover{{color:white;}}")
        entry = (ne,le,tc,de); self._params.append(entry)
        rm.clicked.connect(lambda _,e=entry,r=row: self._remove_param(e,r))
        for w in (ne,le,tc,de,rm): row_l.addWidget(w)
        self.param_list_lay.addWidget(row)

    def _remove_param(self, entry, row):
        if entry in self._params: self._params.remove(entry)
        self.param_list_lay.removeWidget(row); row.deleteLater()

    def get_node_data(self):
        inputs = []
        for ne,tc in self._ports_in:
            ptype = tc.currentText()
            if ptype=="exec": inputs.append({"name":ne.text(),"type":"exec"})
            else: inputs.append({"name":ne.text(),"type":"data","data_type":ptype})
        outputs = []
        for ne,tc in self._ports_out:
            ptype = tc.currentText()
            if ptype=="exec": outputs.append({"name":ne.text(),"type":"exec"})
            else: outputs.append({"name":ne.text(),"type":"data","data_type":ptype})
        params = []
        for ne,le,tc,de in self._params:
            params.append({"name":ne.text(),"label":le.text(),"type":tc.currentText(),
                           "default":de.text()})
        return {
            "id": f"custom_{uuid.uuid4().hex[:8]}",
            "category": self.cat_e.currentText(),
            "title": self.name_e.text(),
            "icon": self.icon_e.text(),
            "description": self.desc_e.text(),
            "inputs": inputs, "outputs": outputs, "params": params,
            "script": self.script_e.toPlainText(),
            "_is_custom": True
        }

# ═══════════════════════════════════════════════════════════════════════════════
# NODE LIBRARY PANEL
# ═══════════════════════════════════════════════════════════════════════════════
CAT_META = {
    "trigger":   ("⚡  Déclencheurs",  "node_trigger"),
    "condition": ("◆  Conditions",     "node_condition"),
    "flow":      ("⟳  Flux",           "node_flow"),
    "action":    ("▶  Actions",        "node_action"),
    "transform": ("⟲  Transformations","node_transform"),
    "data":      ("▦  Données",        "node_data"),
    "variable":  ("𝑥  Variables",      "node_variable"),
    "system":    ("⚙  Système",        "node_system"),
    "network":   ("🌐  Réseau",        "node_network"),
    "output":    ("◉  Sorties",        "node_output"),
    "custom":    ("⭐  Personnalisés",  "node_custom"),
}

class NodeLibraryPanel(QWidget):
    def __init__(self, view):
        super().__init__(); self.view = view
        self.setFixedWidth(248)
        self._build(); TM.changed.connect(self._refresh)

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # header
        hdr = QWidget(); hdr.setFixedHeight(52)
        hl = QHBoxLayout(hdr); hl.setContentsMargins(14,0,14,0)
        title = QLabel("Bibliothèque"); title.setFont(QFont("Segoe UI",11,QFont.Bold))
        hl.addWidget(title)
        lay.addWidget(hdr); self._hdr = hdr; self._title = title

        # search
        sw = QWidget()
        sl = QHBoxLayout(sw); sl.setContentsMargins(10,6,10,6)
        self.search = QLineEdit(); self.search.setPlaceholderText("🔍  Rechercher…")
        self.search.setFixedHeight(30)
        self.search.textChanged.connect(self._filter)
        sl.addWidget(self.search); lay.addWidget(sw); self._sw = sw

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); lay.addWidget(sep); self._sep = sep

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.con = QWidget()
        self.cly = QVBoxLayout(self.con); self.cly.setContentsMargins(8,8,8,8)
        self.cly.setSpacing(3); self.cly.addStretch()
        scroll.setWidget(self.con); lay.addWidget(scroll)
        self._scroll = scroll; self._populate(NODE_CATALOG)
        self._refresh()

    def _refresh(self):
        bd=T.bg_panel().name(); bc=T.bg_card().name(); tp=T.text_primary().name()
        ts=T.text_secondary().name(); bor=T.border().name(); ac=T.accent().name()
        bs=T.bg_surface().name()
        self.setStyleSheet(f"QWidget{{background:{bd};border:none;}}")
        self._hdr.setStyleSheet(f"background:{bc};")
        self._title.setStyleSheet(f"color:{tp};")
        self._sw.setStyleSheet(f"background:{bc};")
        self.search.setStyleSheet(f"""QLineEdit{{background:{bs};border:1px solid {bor};
            border-radius:6px;color:{tp};padding:4px 10px;font-size:10px;}}
            QLineEdit:focus{{border-color:{ac};}}""")
        self._sep.setStyleSheet(f"background:{bor};max-height:1px;")
        self._scroll.setStyleSheet("background:transparent;")
        self._scroll.verticalScrollBar().setStyleSheet(SCROLLBAR_SS)

    def _populate(self, nodes):
        while self.cly.count()>1:
            it=self.cly.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        cats={}
        for n in nodes: cats.setdefault(n["category"],[]).append(n)
        i=0
        for cat, (label, color_fn) in CAT_META.items():
            if cat not in cats: continue
            clbl = QLabel(label); clbl.setFont(QFont("Segoe UI",7,QFont.Bold))
            c = T.cat_color(cat)
            clbl.setStyleSheet(f"color:{c.name()};padding:8px 4px 3px 4px;letter-spacing:1px;")
            self.cly.insertWidget(i,clbl); i+=1
            for nd in cats[cat]:
                btn = self._make_btn(nd, c)
                self.cly.insertWidget(i,btn); i+=1

    def _make_btn(self, nd, color):
        btn = QPushButton(f"  {nd.get('icon','●')}  {nd['title']}")
        btn.setFixedHeight(33); btn.setFont(QFont("Segoe UI",9))
        btn.setCursor(Qt.PointingHandCursor)
        c = color.name(); bd=T.bg_surface().name(); bc=T.bg_card().name()
        tp=T.text_primary().name(); bor=T.border().name()
        btn.setStyleSheet(f"""QPushButton{{background:{bd};border:1px solid {bor};
            border-left:3px solid {c};border-radius:6px;color:{tp};text-align:left;padding:0 10px;}}
            QPushButton:hover{{background:{bc};border-color:{c};}}
            QPushButton:pressed{{background:rgba({color.red()},{color.green()},{color.blue()},30);}}""")
        btn.setToolTip(nd.get("description",""))
        btn.clicked.connect(lambda _, d=nd: self._add_node(d))
        return btn

    def _add_node(self, nd):
        v = self.view
        center = v.mapToScene(v.viewport().rect().center())
        offset = QPointF((len(v.scene().items())%5)*35-70, (len(v.scene().items())%4)*35-52)
        v.scene().addItem(NodeItem(nd, center+offset))

    def _filter(self, txt):
        q = txt.lower()
        f = [n for n in NODE_CATALOG if q in n["title"].lower() or q in n["category"]] if txt else NODE_CATALOG
        self._populate(f)

    def add_custom_node(self, nd):
        NODE_CATALOG.append(nd)
        CUSTOM_NODES.append(nd)
        save_custom_nodes(CUSTOM_NODES)
        self._populate(NODE_CATALOG)

# ═══════════════════════════════════════════════════════════════════════════════
# LOG PANEL
# ═══════════════════════════════════════════════════════════════════════════════
class LogPanel(QWidget):
    def __init__(self):
        super().__init__(); self._build(); TM.changed.connect(self._refresh)

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        hdr=QWidget(); hdr.setFixedHeight(34)
        hl=QHBoxLayout(hdr); hl.setContentsMargins(12,0,12,0)
        lbl=QLabel("Console"); lbl.setFont(QFont("Segoe UI",9,QFont.Bold))
        cl=QPushButton("Effacer"); cl.setFixedHeight(22); cl.setFont(QFont("Segoe UI",8))
        cl.setCursor(Qt.PointingHandCursor)
        hl.addWidget(lbl); hl.addStretch(); hl.addWidget(cl)
        lay.addWidget(hdr); self._hdr=hdr; self._cl=cl; self._lbl=lbl
        self.log_text=QTextEdit(); self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas",9))
        lay.addWidget(self.log_text)
        cl.clicked.connect(self.log_text.clear)
        self._refresh()
        self.log("🚀 Tryxee Automations v2 initialisé","success")
        self.log("ℹ   Double-clic sur l'en-tête d'un nœud pour le déployer","info")
        self.log("ℹ   Cliquez sur un nœud pour ouvrir ses propriétés","info")

    def _refresh(self):
        bd=T.bg_deep().name(); bc=T.bg_card().name(); ts=T.text_secondary().name(); bor=T.border().name()
        tp=T.text_primary().name()
        self.setStyleSheet(f"QWidget{{background:{T.bg_panel().name()};border:none;}}")
        self._hdr.setStyleSheet(f"background:{bc};")
        self._lbl.setStyleSheet(f"color:{ts};background:transparent;")
        self._cl.setStyleSheet(f"""QPushButton{{background:transparent;border:1px solid {bor};
            border-radius:4px;color:{ts};padding:0 8px;}}QPushButton:hover{{background:{bor};color:{tp};}}""")
        self.log_text.setStyleSheet(f"QTextEdit{{background:{bd};color:{ts};border:none;padding:8px;}}")
        self.log_text.verticalScrollBar().setStyleSheet(SCROLLBAR_SS)

    def log(self, msg, level="default"):
        c={"success":"#10b981","info":"#3b82f6","warning":"#f59e0b","error":"#ef4444","default":"#7a8ba0"}.get(level,"#7a8ba0")
        self.log_text.append(f'<span style="color:{c};">{msg}</span>')

# ═══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════════
class ThemeSwitch(QWidget):
    def __init__(self):
        super().__init__(); self.setFixedSize(52,26); self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Basculer thème clair/sombre")

    def mousePressEvent(self, e): TM.toggle()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        dark = TM.is_dark()
        track = QColor("#252d3d") if dark else QColor("#c0c8d8")
        p.setBrush(QBrush(track)); p.setPen(Qt.NoPen)
        p.drawRoundedRect(0,3,52,20,10,10)
        knob_x = 28 if dark else 4
        knob_c = QColor("#00d4ff") if dark else QColor("#f59e0b")
        p.setBrush(QBrush(knob_c)); p.drawEllipse(knob_x,2,22,22)
        p.setPen(QPen(QColor("#ffffff"))); p.setFont(QFont("Segoe UI",8))
        p.drawText(QRect(knob_x,2,22,22), Qt.AlignCenter, "🌙" if dark else "☀")

class TopBar(QWidget):
    run_sig   = pyqtSignal()
    import_sig   = pyqtSignal()
    save_sig  = pyqtSignal()
    clear_sig = pyqtSignal()
    custom_sig= pyqtSignal()

    def __init__(self):
        super().__init__(); self.setFixedHeight(52); self._build()
        TM.changed.connect(self._refresh)

    def _build(self):
        lay = QHBoxLayout(self); lay.setContentsMargins(16,0,16,0); lay.setSpacing(10)
        self.logo = QLabel("◈"); self.logo.setFont(QFont("Segoe UI",16))
        self.name = QLabel("Tryxee Automations"); self.name.setFont(QFont("Segoe UI",13,QFont.Bold))
        self.ver  = QLabel("v2.0"); self.ver.setFont(QFont("Segoe UI",8))
        lay.addWidget(self.logo); lay.addWidget(self.name); lay.addWidget(self.ver)
        lay.addStretch()
        self.btns_data = [
            ("▶  Exécuter",        T.success,  self.run_sig),
            ("📤 Export",          T.info,     self.save_sig),
            ("📥 Import",          T.info,     self.import_sig),
            ("⭐ Nœud Perso",      T.warning,  self.custom_sig),
            ("🗑  Effacer",         T.danger,   self.clear_sig),
        ]
        self._btns = []
        for text, cfn, sig in self.btns_data:
            b=QPushButton(text); b.setFixedHeight(34); b.setFont(QFont("Segoe UI",9,QFont.Bold))
            b.setCursor(Qt.PointingHandCursor); b.clicked.connect(sig.emit)
            self._btns.append((b,cfn)); lay.addWidget(b)
        lay.addSpacing(8)
        self.theme_sw = ThemeSwitch(); lay.addWidget(self.theme_sw)
        lay.addSpacing(4)
        self.zoom_lbl = QLabel("100%"); self.zoom_lbl.setFont(QFont("Consolas",9))
        self.zoom_lbl.setFixedWidth(50); self.zoom_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.zoom_lbl)
        self._refresh()

    def _refresh(self):
        bc=T.bg_card().name(); tp=T.text_primary().name(); ts=T.text_secondary().name()
        ac=T.accent().name(); bor=T.border().name()
        self.setStyleSheet(f"QWidget{{background:{bc};border-bottom:1px solid {bor};}}")
        self.logo.setStyleSheet(f"color:{ac};background:transparent;border:none;")
        self.name.setStyleSheet(f"color:{tp};background:transparent;border:none;")
        self.ver.setStyleSheet(f"color:{ac};background:transparent;border:none;")
        self.zoom_lbl.setStyleSheet(f"color:{ts};background:transparent;border:none;")
        for btn,cfn in self._btns:
            c=cfn(); cn=c.name()
            btn.setStyleSheet(f"""QPushButton{{background:rgba({c.red()},{c.green()},{c.blue()},18);
                border:1px solid {cn};border-radius:7px;color:{cn};padding:0 14px;}}
                QPushButton:hover{{background:{cn};color:#0a0c10;}}
                QPushButton:pressed{{background:{c.darker(120).name()};}}""")

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED STYLES (rebuilt on theme change)
# ═══════════════════════════════════════════════════════════════════════════════
def _build_shared_styles():
    global SCROLLBAR_SS, MENU_SS
    SCROLLBAR_SS = f"""QScrollBar:vertical{{background:{T.bg_deep().name()};width:6px;border-radius:3px;}}
        QScrollBar::handle:vertical{{background:{T.border_light().name()};border-radius:3px;min-height:20px;}}
        QScrollBar::handle:vertical:hover{{background:{T.text_dim().name()};}}
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}"""
    MENU_SS = f"""QMenu{{background:{T.bg_card().name()};border:1px solid {T.border_light().name()};
        border-radius:8px;padding:6px;color:{T.text_primary().name()};font-family:'Segoe UI';font-size:10px;}}
        QMenu::item{{padding:7px 16px 7px 12px;border-radius:5px;}}
        QMenu::item:selected{{background:{T.bg_surface().name()};color:white;}}
        QMenu::separator{{height:1px;background:{T.border().name()};margin:4px 8px;}}"""

SCROLLBAR_SS = ""; MENU_SS = ""
_build_shared_styles()
TM.changed.connect(_build_shared_styles)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("tryxee.ico"))
        self.setWindowTitle("Tryxee Automations v2")
        self.setMinimumSize(1280,720); self.resize(1520,920)
        self._build_ui()
        #self.scene.selectionChanged.connect(lambda: (self.properties_panel.show_node(self.scene.selectedItems()[0]) if self.scene.selectedItems() else None))
        
        # connecter les boutons topbar
        #self.topbar.run_sig.connect(self._run)
        #self.topbar.save_sig.connect(self._save)     # ou _save en fonction du nom que tu veux
        #self.topbar.custom_sig.connect(self._import)   # si tu souhaites réutiliser le bouton "Nœud Perso" pour importer
        #self.topbar.clear_sig.connect(self._clear)
        
        self._load_example()
        QTimer(self, timeout=self._tick).start(200)
        TM.changed.connect(self._refresh_theme)
        self._refresh_theme()

    def _build_ui(self):
        cw=QWidget(); self.setCentralWidget(cw)
        root=QVBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        self.topbar = TopBar()
        self.topbar.run_sig.connect(self._run)
        self.topbar.import_sig.connect(self._import)
        self.topbar.save_sig.connect(self._save)
        self.topbar.clear_sig.connect(self._clear)
        self.topbar.custom_sig.connect(self._new_custom_node)
        root.addWidget(self.topbar)

        mid = QWidget(); mid.setObjectName("mid")
        mlay = QHBoxLayout(mid); mlay.setContentsMargins(0,0,0,0); mlay.setSpacing(0)
        root.addWidget(mid)

        self.scene = BlueprintScene()
        self.view  = BlueprintView(self.scene)
        self.scene.node_selected.connect(self._sel_node)
        self.scene.node_deselected.connect(self._desel_node)

        self.library = NodeLibraryPanel(self.view)

        # canvas + log splitter
        right = QWidget()
        rlay = QVBoxLayout(right); rlay.setContentsMargins(0,0,0,0); rlay.setSpacing(0)
        vsplit = QSplitter(Qt.Vertical)
        vsplit.setHandleWidth(3); vsplit.addWidget(self.view)
        self.log_panel = LogPanel(); self.log_panel.setMinimumHeight(80)
        vsplit.addWidget(self.log_panel); vsplit.setStretchFactor(0,4)
        rlay.addWidget(vsplit)

        # dividers + props panel
        div1=QFrame(); div1.setFrameShape(QFrame.VLine); div1.setObjectName("div")
        div2=QFrame(); div2.setFrameShape(QFrame.VLine); div2.setObjectName("div")
        self.props = PropertiesPanel()
        self.props.node_focus_requested.connect(self._focus_node)

        mlay.addWidget(self.library)
        mlay.addWidget(div1); mlay.addWidget(right)
        mlay.addWidget(div2); mlay.addWidget(self.props)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("  Double-clic sur en-tête = déployer  •  Clic nœud = propriétés  •  Molette = zoom  •  Alt+Drag = pan  •  F = tout afficher")

    def _refresh_theme(self):
        bd=T.bg_deep().name(); bor=T.border().name(); bc=T.bg_card().name()
        self.centralWidget().setStyleSheet(f"QWidget{{background:{bd};}}")
        self.findChild(QWidget,"mid").setStyleSheet("border:none;")
        for d in self.findChildren(QFrame,"div"):
            d.setStyleSheet(f"background:{bor};max-width:1px;")
        self.status.setStyleSheet(f"""QStatusBar{{background:{bc};color:{T.text_dim().name()};
            font-size:10px;font-family:'Segoe UI';border-top:1px solid {bor};}}""")
        # Refresh scene background
        self.scene.update()

    def _load_example(self):
        ex = [
            (next(n for n in NODE_CATALOG if n["id"]=="trigger_schedule"), QPointF(-380,-60)),
            (next(n for n in NODE_CATALOG if n["id"]=="cond_if"),           QPointF(-80, -60)),
            (next(n for n in NODE_CATALOG if n["id"]=="action_email"),      QPointF(230,-160)),
            (next(n for n in NODE_CATALOG if n["id"]=="action_notification"),QPointF(230,  40)),
            (next(n for n in NODE_CATALOG if n["id"]=="var_string"),         QPointF(-380, 120)),
            (next(n for n in NODE_CATALOG if n["id"]=="out_log"),            QPointF(530,-160)),
        ]
        nodes=[]
        for nd,pos in ex:
            n=NodeItem(nd,pos); self.scene.addItem(n); nodes.append(n)
        def connect(s,t):
            c=ConnectionItem(s); c.target_port=t; c.update_path()
            s.connections.append(c); t.connections.append(c)
            s.mark_connected(); t.mark_connected(); self.scene.addItem(c)
        connect(nodes[0].output_ports[0], nodes[1].input_ports[0])
        connect(nodes[1].output_ports[0], nodes[2].input_ports[0])
        connect(nodes[1].output_ports[1], nodes[3].input_ports[0])
        connect(nodes[4].output_ports[0], nodes[2].input_ports[3])
        connect(nodes[2].output_ports[0], nodes[5].input_ports[0])
        self.view.centerOn(100,0)

    def _tick(self):
        self.topbar.zoom_lbl.setText(f"{int(self.view._zoom*100)}%")

    def _sel_node(self, node):
        self.props.show_node(node)
        self.status.showMessage(f"  ◈  {node.title}  [{node.category}]  —  double-clic sur en-tête pour déployer")

    def _desel_node(self):
        self.props.close_panel()
        self.status.showMessage("  Double-clic sur en-tête = déployer  •  Clic nœud = propriétés  •  Molette = zoom  •  Alt+Drag = pan  •  F = tout afficher")

    def _focus_node(self, node):
        if not node: return
        self.scene.clearSelection(); node.setSelected(True)
        self.view.centerOn(node)

    def _run(self):
        try:
            runner = BackendRunner(self.scene)
            runner.load_functions()

            results = runner.execute_all()

            executed = len(results) if isinstance(results, dict) else 0

            if isinstance(results, dict):
                for nid, out in results.items():
                    self.log_panel.log(
                        f"▶ {nid} → {str(out)[:120]}",
                        "info"
                    )

            self.log_panel.log(
                f"✓ Flux terminé — {executed} nœuds exécutés",
                "success"
            )

            self.status.showMessage(
                f"✓ Exécuté — {executed} nœuds"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log_panel.log(
                f"❌ Erreur exécution : {e}",
                "danger"
            )
            
    def _save(self):
        import json
        from PyQt5.QtWidgets import QFileDialog

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter blueprint",
            "",
            "Blueprint (*.json)"
        )
        if not fname:
            return

        nodes = []
        conns = []

        for it in self.scene.items():
            if isinstance(it, NodeItem):
                node_data = dict(it.node_data or {})
                function_id = getattr(it, "backend_id", node_data.get("id"))
                instance_id = getattr(it, "instance_id", None) or str(uuid.uuid4())

                node_data["id"] = function_id
                node_data["instance_id"] = instance_id

                nodes.append({
                    "instance_id": instance_id,
                    "function_id": function_id,
                    "node_data": node_data,
                    "params": dict(getattr(it, "node_params", {})),
                    "expanded": bool(getattr(it, "expanded", False)),
                    "x": float(it.pos().x()),
                    "y": float(it.pos().y()),
                })

        seen = set()
        for it in self.scene.items():
            if isinstance(it, ConnectionItem) and getattr(it, "source_port", None) and getattr(it, "target_port", None):
                sp = it.source_port
                tp = it.target_port
                sid = getattr(getattr(sp, "node", None), "instance_id", None)
                tid = getattr(getattr(tp, "node", None), "instance_id", None)
                if not sid or not tid:
                    continue

                key = (sid, sp.name, tid, tp.name)
                if key in seen:
                    continue
                seen.add(key)

                conns.append({
                    "src_id": sid,
                    "src_port": sp.name,
                    "tgt_id": tid,
                    "tgt_port": tp.name
                })

        data = {
            "version": 2,
            "nodes": nodes,
            "connections": conns
        }

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.log_panel.log(f"📤 Blueprint exporté ({len(nodes)} nœuds)", "success")

    def _import(self):
        import json
        from PyQt5.QtWidgets import QFileDialog

        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Importer blueprint",
            "",
            "Blueprint (*.json)"
        )
        if not fname:
            return

        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.scene.clear()
        id_map = {}

        def _find_port(node, port_name, inputs=False):
            if not node:
                return None
            ports = (node.input_ports + getattr(node, "param_ports", [])) if inputs else node.output_ports
            for p in ports:
                if p.name == port_name:
                    return p
            for p in ports:
                if str(p.name).strip().lower() == str(port_name).strip().lower():
                    return p
            return None

        # recreate nodes
        for n in data.get("nodes", []):
            node_data = dict(n.get("node_data", {}) or {})
            function_id = n.get("function_id") or node_data.get("id") or str(uuid.uuid4())
            instance_id = n.get("instance_id") or node_data.get("instance_id") or str(uuid.uuid4())

            node_data["id"] = function_id
            node_data["instance_id"] = instance_id

            node = NodeItem(node_data)
            node.backend_id = function_id
            node.instance_id = instance_id
            node.node_data["id"] = function_id
            node.node_data["instance_id"] = instance_id
            node.node_params = dict(n.get("params", {}) or {})
            node.expanded = bool(n.get("expanded", False))
            node._update_height()

            self.scene.addItem(node)
            node.setPos(float(n.get("x", 0)), float(n.get("y", 0)))
            node.update()

            id_map[instance_id] = node

        # recreate connections
        for c in data.get("connections", []):
            src_node = id_map.get(c.get("src_id"))
            tgt_node = id_map.get(c.get("tgt_id"))
            if not src_node or not tgt_node:
                continue

            src_port = _find_port(src_node, c.get("src_port"), inputs=False)
            tgt_port = _find_port(tgt_node, c.get("tgt_port"), inputs=True)
            if not src_port or not tgt_port:
                continue

            conn = ConnectionItem(src_port)
            conn.target_port = tgt_port
            conn.update_path()
            self.scene.addItem(conn)

            src_port.connections.append(conn)
            tgt_port.connections.append(conn)
            src_port.mark_connected()
            tgt_port.mark_connected()

        self.log_panel.log(f"📥 Blueprint importé ({len(id_map)} nœuds)", "success")

    def _clear(self):
        if QMessageBox.question(self,"Effacer","Effacer tout le canvas ?",
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.scene.clear(); self.log_panel.log("🗑  Canvas effacé","warning")

    def _new_custom_node(self):
        dlg = CustomNodeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            nd = dlg.get_node_data()
            self.library.add_custom_node(nd)
            n = NodeItem(nd, self.view.mapToScene(self.view.viewport().rect().center()))
            self.scene.addItem(n)
            self.log_panel.log(f"⭐  Nœud personnalisé créé : {nd['title']}","success")

# backend runner — charge functions.py et exécute fonctions par id
class BackendRunner:
    def __init__(self, scene, functions_path=None):
        """
        scene: QGraphicsScene instance containing NodeItem objects
        functions_path: optional path to functions.py; default = same folder as blueprint_app.py
        """
        self.scene = scene
        base = os.path.dirname(os.path.abspath(__file__))
        self.functions_path = functions_path or os.path.join(base, "functions.py")
        self.functions = {}   # mapping id_str -> callable
        self.module = None
        self.load_functions()

    def load_functions(self):
        """Load/Reload functions.py. Accepts either a dict named 'functions' or a dict returned by register()."""
        if not os.path.exists(self.functions_path):
            print("BackendRunner: functions.py not found at", self.functions_path)
            self.functions = {}
            return
        spec = importlib.util.spec_from_file_location("bp_functions", self.functions_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.module = module
        funcs = {}
        # preferred: module.functions must be a dict {id: callable}
        if hasattr(module, "functions") and isinstance(module.functions, dict):
            funcs.update(module.functions)
        # also accept a function `register_functions()` that returns a dict
        if hasattr(module, "register_functions") and callable(module.register_functions):
            try:
                result = module.register_functions()
                if isinstance(result, dict):
                    funcs.update(result)
            except Exception as e:
                print("Error calling register_functions():", e)
        # finally, accept any callable attributes whose name equals an id (not recommended)
        # set final map
        self.functions = funcs

    def find_node_by_id(self, backend_id):
        for it in self.scene.items():
            # only NodeItem instances (best-effort detection)
            if type(it).__name__ == "NodeItem" and getattr(it, "backend_id", None) == backend_id:
                return it
        return None

    def collect_inputs(self, node):
        """
        Robust collect_inputs:
        - combine input_ports and param_ports
        - normalize names (strip + lower) to match node_params reliably
        - prefer runtime last_outputs from source node, then source.node_params, then node.node_params
        """
        def _norm(x):
            return str(x).strip().lower() if x is not None else ""

        inputs = {}

        # normalized map of this node's params for quick lookup
        node_params = getattr(node, "node_params", {}) or {}
        node_param_map = { _norm(k): v for k,v in node_params.items() }

        ports = list(getattr(node, "input_ports", [])) + list(getattr(node, "param_ports", []))

        for p in ports:
            key = p.name
            nkey = _norm(key)
            val = None

            # 1) if connected: try to read from source node outputs / params
            if getattr(p, "connections", None):
                conn = p.connections[0]
                src = getattr(conn, "source_port", None)
                if src and getattr(src, "node", None):
                    src_node = src.node

                    # try runtime outputs first
                    src_outputs = getattr(src_node, "last_outputs", {}) or {}
                    # direct by port name
                    val = src_outputs.get(src.name)
                    # try normalized keys if still None
                    if val is None:
                        src_out_map = { _norm(k): v for k,v in src_outputs.items() }
                        val = src_out_map.get(_norm(src.name))

                    # fallback to source node params
                    if val is None and hasattr(src_node, "node_params"):
                        sp = src_node.node_params or {}
                        sp_map = { _norm(k): v for k,v in sp.items() }
                        # try matching by port name then common keys
                        val = sp_map.get(_norm(src.name))
                        if val is None:
                            val = sp_map.get("value")

            # 2) if still None: use this node's parameter with same name
            if val is None:
                val = node_param_map.get(nkey)

            # guard: convert literal 'None' strings to None
            if isinstance(val, str) and val.strip().lower() == "none":
                val = None

            inputs[key] = val

        # debug — helpful to see exactly what each node receives
        try:
            print(f"[BackendRunner] collect_inputs for node {getattr(node,'backend_id',None)} -> {inputs}")
        except Exception:
            pass

        return inputs

    def execute_node(self, node):
        """Run the backend function tied to this node."""
        fid = getattr(node, "backend_id", None)
        if not fid:
            raise KeyError("Node has no backend id")

        func = self.functions.get(fid)
        if not callable(func):
            raise KeyError(f"No backend function registered for id {fid!r}")

        inputs = self.collect_inputs(node)

        # 🔥 PARAMS runtime
        params = dict(getattr(node, "node_params", {}) or {})

        # 🔥 DEBUG IMPORTANT
        print("=== EXEC NODE ===")
        print("NODE:", fid)
        print("PARAMS:", params)
        print("INPUTS:", inputs)

        try:
            result = func(inputs, params)
        except Exception as e:
            print(f"Error running backend function for node {node.title} ({fid}): {e}")
            raise

        if isinstance(result, dict):
            node.set_outputs(result)

        return result

    def execute_node_by_id(self, backend_id):
        node = self.find_node_by_id(backend_id)
        if not node:
            raise KeyError("No node with id " + str(backend_id))
        return self.execute_node(node)

    def execute_flow(self):
        """
        Execute nodes following flow connections (exec ports preferred).
        Strategy:
         - Build adjacency using output connections (exec or data).
         - Start from trigger nodes (backend id startswith 'trigger') or nodes without incoming edges.
         - Depth-first traversal, executing each node once.
        """
        # collect nodes
        nodes = [it for it in list(self.scene.items()) if type(it).__name__ == "NodeItem"]
        # build incoming edges map and adjacency list
        incoming = {n: set() for n in nodes}
        adj = {n: [] for n in nodes}

        # build edges: use output connections (all types) as directed edges
        for it in nodes:
            for outp in getattr(it, 'output_ports', []):
                for c in getattr(outp, 'connections', []):
                    tgt = getattr(c, 'target_port', None)
                    if not tgt or not getattr(tgt, 'node', None):
                        continue
                    tgt_node = tgt.node
                    adj[it].append(tgt_node)
                    incoming[tgt_node].add(it)

        # find start nodes: triggers or nodes without incoming edges
        starts = [n for n in nodes if (getattr(n, 'backend_id', '').startswith('trigger') or len(incoming.get(n, [])) == 0)]

        visited = set()
        results = {}

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            try:
                out = self.execute_node(node)
                results[node.backend_id] = out
            except KeyError:
                # no backend function registered for this node -> skip execution
                pass
            except Exception as e:
                print("Execution error for node", getattr(node, "title", None), e)
            for nb in adj.get(node, []):
                dfs(nb)

        for s in starts:
            dfs(s)

        return results

    def execute_all(self):
        """
        Backwards-compatible execute_all: delegate to execute_flow which
        provides a flow-aware execution order.
        """
        return self.execute_flow()

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Tryxee Automations")
    app.setStyle("Fusion")

    def apply_palette():
        pal = QPalette()
        pal.setColor(QPalette.Window,          T.bg_deep())
        pal.setColor(QPalette.WindowText,      T.text_primary())
        pal.setColor(QPalette.Base,            T.bg_surface())
        pal.setColor(QPalette.AlternateBase,   T.bg_card())
        pal.setColor(QPalette.Text,            T.text_primary())
        pal.setColor(QPalette.Button,          T.bg_card())
        pal.setColor(QPalette.ButtonText,      T.text_primary())
        pal.setColor(QPalette.Highlight,       T.accent())
        pal.setColor(QPalette.HighlightedText, QColor("#0a0c10"))
        app.setPalette(pal)
    apply_palette()
    TM.changed.connect(apply_palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
