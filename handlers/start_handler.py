from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import BOT_NAME, AVAILABLE_LANGUAGES
from utils.translations import get_text
from database.sqlite_client import get_or_create_user
from database.credits_client import get_user_credits

# Zabezpieczony import z awaryjnym fallbackiem
try:
    from utils.referral import use_referral_code
except ImportError:
    # Fallback jeśli import nie zadziała
    def use_referral_code(user_id, code):
        """
        Prosta implementacja awaryjnego fallbacku dla use_referral_code
        """
        # Jeśli kod ma format REF123, wyodrębnij ID polecającego
        if code.startswith("REF") and code[3:].isdigit():
            referrer_id = int(code[3:])
            # Sprawdź, czy użytkownik nie używa własnego kodu
            if referrer_id == user_id:
                return False, None
            # Dodanie kredytów zostałoby implementowane tutaj w prawdziwym przypadku
            return True, referrer_id
        return False, None

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Wyświetla wybór języka przy pierwszym uruchomieniu
    """
    # Utwórz przyciski dla każdego języka
    keyboard = []
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"start_lang_{lang_code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Użyj neutralnego języka dla pierwszej wiadomości
    welcome_message = f"🌐 Wybierz język / Choose language / Выберите язык:"
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

def get_user_language(context, user_id):
    """
    Pobiera język użytkownika z kontekstu lub bazy danych
    """
    # Sprawdź, czy język jest zapisany w kontekście
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'language' in context.chat_data['user_data'][user_id]:
        return context.chat_data['user_data'][user_id]['language']
    
    # Jeśli nie, pobierz z bazy danych
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Zmieniamy z language_code na selected_language - to jest kluczowa zmiana
        cursor.execute("SELECT selected_language FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Zapisz w kontekście na przyszłość
            if 'user_data' not in context.chat_data:
                context.chat_data['user_data'] = {}
            
            if user_id not in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id] = {}
            
            context.chat_data['user_data'][user_id]['language'] = result[0]
            return result[0]
    except Exception as e:
        print(f"Błąd pobierania języka z bazy: {e}")
    
    # Domyślny język, jeśli nie znaleziono w bazie
    return None  # Zwracamy None zamiast "pl", żeby wymusić wybór języka

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługuje wybór języka przez użytkownika
    """
    query = update.callback_query
    
    if not query.data.startswith("start_lang_"):
        return
    
    language = query.data[11:]  # Usuń prefix "start_lang_"
    user_id = query.from_user.id
    
    print(f"Obsługa wyboru języka: użytkownik {user_id} wybrał język {language}")
    
    # Zapisz język w bazie danych - w kolumnie selected_language
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Sprawdź, czy użytkownik istnieje
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            # Aktualizuj istniejącego użytkownika
            cursor.execute("UPDATE users SET selected_language = ? WHERE id = ?", (language, user_id))
        else:
            # Dodaj nowego użytkownika (to też powinno być obsłużone przez get_or_create_user)
            cursor.execute("INSERT INTO users (id, selected_language) VALUES (?, ?)", (user_id, language))
        
        conn.commit()
        conn.close()
        print(f"Język {language} zapisany w bazie danych dla użytkownika {user_id}")
    except Exception as e:
        print(f"Błąd zapisywania języka: {e}")
    
    # Zapisz język w kontekście
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user_id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user_id] = {}
    
    context.chat_data['user_data'][user_id]['language'] = language
    
    # Pobierz stan kredytów
    credits = get_user_credits(user_id)
    
    # Przygotowanie wiadomości powitalnej
    welcome_text = get_text("welcome_message", language, bot_name=BOT_NAME, credits=credits)
    
    # Dodajemy menu inline do wiadomości powitalnej
    from handlers.menu_system import build_main_menu
    reply_markup = build_main_menu(language)
    
    try:
        # Aktualizuj wiadomość
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        print(f"Wiadomość powitalna została zaktualizowana dla użytkownika {user_id}")
    except Exception as e:
        print(f"Błąd podczas aktualizacji wiadomości: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Obsługa komendy /start
    Tworzy lub pobiera użytkownika z bazy danych i wyświetla wiadomość powitalną
    """
    user = update.effective_user
    
    # Pobierz lub utwórz użytkownika w bazie danych
    user_data = get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    # Sprawdź, czy istnieje kod referencyjny w argumencie start
    if context.args and len(context.args) > 0:
        start_param = context.args[0]
        
        # Obsługa kodu referencyjnego (format: ref_XXXXX)
        if start_param.startswith("ref_"):
            ref_code = start_param[4:]
            success, referrer_id = use_referral_code(user.id, ref_code)
            
            if success:
                # Używamy domyślnego języka dla komunikatu o kodzie referencyjnym
                await update.message.reply_text(
                    get_text("referral_success", "pl", credits=25),
                    parse_mode=ParseMode.MARKDOWN
                )
    
    # Pobierz język z bazy danych - z kolumny selected_language
    selected_language = None
    try:
        from database.sqlite_client import sqlite3, DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT selected_language FROM users WHERE id = ?", (user.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            selected_language = result[0]
    except Exception as e:
        print(f"Błąd pobierania języka z bazy: {e}")
    
    # Jeśli użytkownik nie ma jeszcze wybranego języka, pokaż wybór języka
    if not selected_language:
        return await show_language_selection(update, context)
    
    # Zapisz język w kontekście
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    if user.id not in context.chat_data['user_data']:
        context.chat_data['user_data'][user.id] = {}
    
    context.chat_data['user_data'][user.id]['language'] = selected_language
    
    # Pobierz stan kredytów
    credits = get_user_credits(user.id)
    
    # Przygotowanie wiadomości powitalnej
    welcome_text = get_text("welcome_message", selected_language, bot_name=BOT_NAME, credits=credits)
    
    # Dodajemy menu inline do wiadomości powitalnej
    from handlers.menu_system import build_main_menu
    reply_markup = build_main_menu(selected_language)
    
    await update.message.reply_text(
        welcome_text, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )