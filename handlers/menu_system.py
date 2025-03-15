"""
Kompleksowy system menu inline dla bota Telegram
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from config import BOT_NAME, CHAT_MODES, AVAILABLE_MODELS, CREDIT_PACKAGES
from utils.translations import get_text
from database.credits_client import get_user_credits

# Dictionary to map menu levels to their parent levels for back navigation
MENU_HIERARCHY = {
    "main": None,  # Main menu has no parent
    "chat_modes": "main",
    "notes": "main",
    "reminders": "main",
    "credits": "main",
    "account": "main",
    "settings": "main",
    "help": "main",
    # Sub-levels
    "view_notes": "notes",
    "create_note": "notes",
    "view_reminders": "reminders",
    "create_reminder": "reminders",
    "buy_credits": "credits",
    "enter_code": "credits",
    "export": "account",
    "language": "settings",
    "model": "settings",
    "name": "settings",
    "commands": "help",
    "faq": "help",
}

#################################
# Menu building functions
#################################

def build_main_menu(language):
    """Build the main menu with all primary options"""
    keyboard = [
        [
            InlineKeyboardButton(get_text("menu_chat_mode", language), 
                                callback_data="menu_level_chat_modes"),
            InlineKeyboardButton(get_text("menu_newchat", language), 
                                callback_data="menu_action_newchat")
        ],
        [
            InlineKeyboardButton(get_text("menu_notes", language), 
                                callback_data="menu_level_notes"),
            InlineKeyboardButton(get_text("menu_reminders", language), 
                                callback_data="menu_level_reminders")
        ],
        [
            InlineKeyboardButton(get_text("menu_credits", language), 
                                callback_data="menu_level_credits"),
            InlineKeyboardButton(get_text("menu_status", language), 
                                callback_data="menu_level_account")
        ],
        [
            InlineKeyboardButton("⚙️ " + get_text("menu_settings", language), 
                                callback_data="menu_level_settings"),
            InlineKeyboardButton("❓ " + get_text("menu_help", language), 
                                callback_data="menu_level_help")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_chat_modes_menu(language):
    """Build menu with available chat modes"""
    keyboard = []
    
    # Add buttons for all chat modes, 2 per row
    mode_buttons = []
    for mode_id, mode_info in CHAT_MODES.items():
        # Choose name in appropriate language
        mode_name = mode_info['name']
        if language == 'en' and 'name_en' in mode_info:
            mode_name = mode_info['name_en']
        elif language == 'ru' and 'name_ru' in mode_info:
            mode_name = mode_info['name_ru']
        
        # Create button with cost info
        button = InlineKeyboardButton(
            f"{mode_name} ({mode_info['credit_cost']})", 
            callback_data=f"menu_action_set_mode_{mode_id}"
        )
        
        mode_buttons.append(button)
        
        # Add row after every 2 buttons
        if len(mode_buttons) == 2:
            keyboard.append(mode_buttons)
            mode_buttons = []
    
    # Add any remaining buttons
    if mode_buttons:
        keyboard.append(mode_buttons)
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                            callback_data="menu_back_to_main")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_notes_menu(language):
    """Build the notes submenu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 " + get_text("view_notes", language, default="Zobacz notatki"), 
                                callback_data="menu_action_view_notes")
        ],
        [
            InlineKeyboardButton("✏️ " + get_text("create_note", language, default="Utwórz notatkę"), 
                                callback_data="menu_action_create_note")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_reminders_menu(language):
    """Build the reminders submenu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 " + get_text("view_reminders", language, default="Zobacz przypomnienia"), 
                                callback_data="menu_action_view_reminders")
        ],
        [
            InlineKeyboardButton("⏰ " + get_text("create_reminder", language, default="Utwórz przypomnienie"), 
                                callback_data="menu_action_create_reminder")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_credits_menu(language, user_id):
    """Build the credits submenu with current balance"""
    credits = get_user_credits(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton(f"💰 {get_text('balance', language, default='Saldo')}: {credits} {get_text('credits', language)}", 
                                callback_data="menu_action_none")
        ],
        [
            InlineKeyboardButton("🛒 " + get_text("buy_credits", language, default="Kup kredyty"), 
                                callback_data="menu_level_buy_credits")
        ],
        [
            InlineKeyboardButton("🎟️ " + get_text("enter_code", language, default="Wprowadź kod"), 
                                callback_data="menu_action_enter_code")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_buy_credits_menu(language):
    """Build menu with credit packages to buy"""
    keyboard = []
    
    # Add buttons for all credit packages
    for package in CREDIT_PACKAGES:
        keyboard.append([
            InlineKeyboardButton(
                f"{package['name']} - {package['credits']} {get_text('credits', language)} ({package['price']} PLN)", 
                callback_data=f"menu_action_buy_package_{package['id']}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                            callback_data="menu_back_to_credits")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_account_menu(language):
    """Build the account submenu"""
    keyboard = [
        [
            InlineKeyboardButton("📊 " + get_text("view_stats", language, default="Zobacz statystyki"), 
                                callback_data="menu_action_view_stats")
        ],
        [
            InlineKeyboardButton("📤 " + get_text("export_conversation", language, default="Eksportuj rozmowę"), 
                                callback_data="menu_action_export")
        ],
        [
            InlineKeyboardButton("🔄 " + get_text("restart_bot", language, default="Zrestartuj bota"), 
                                callback_data="menu_action_restart")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_settings_menu(language):
    """Build the settings submenu"""
    keyboard = [
        [
            InlineKeyboardButton("🌐 " + get_text("settings_language", language), 
                                callback_data="menu_level_language")
        ],
        [
            InlineKeyboardButton("🤖 " + get_text("settings_model", language), 
                                callback_data="menu_level_model")
        ],
        [
            InlineKeyboardButton("👤 " + get_text("settings_name", language), 
                                callback_data="menu_action_set_name")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def build_language_menu(language):
    """Build menu with available languages"""
    keyboard = []
    
    # Add buttons for all languages
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{lang_name} {'✓' if lang_code == language else ''}", 
                callback_data=f"menu_action_set_language_{lang_code}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                            callback_data="menu_back_to_settings")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_model_menu(language):
    """Build menu with available AI models"""
    keyboard = []
    
    # Add buttons for all models
    for model_id, model_name in AVAILABLE_MODELS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{model_name}", 
                callback_data=f"menu_action_set_model_{model_id}"
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                            callback_data="menu_back_to_settings")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def build_help_menu(language):
    """Build the help submenu"""
    keyboard = [
        [
            InlineKeyboardButton("📋 " + get_text("commands_list", language, default="Lista komend"), 
                                callback_data="menu_action_show_commands")
        ],
        [
            InlineKeyboardButton("❓ " + get_text("faq", language, default="FAQ"), 
                                callback_data="menu_action_faq")
        ],
        [
            InlineKeyboardButton("🔙 " + get_text("back_button", language, default="Wstecz"), 
                                callback_data="menu_back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

#################################
# Menu navigation handler
#################################

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Master handler for all menu callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    # Get user language
    language = "pl"  # Default fallback
    if 'user_data' in context.chat_data and user_id in context.chat_data['user_data'] and 'language' in context.chat_data['user_data'][user_id]:
        language = context.chat_data['user_data'][user_id]['language']
    
    await query.answer()  # Acknowledge the button press
    
    #################################
    # Navigation between menu levels
    #################################
    
    # Handle menu level navigation (switching between menu sections)
    if callback_data.startswith("menu_level_"):
        level = callback_data[11:]  # Extract level name after "menu_level_"
        
        # Update user's menu state
        if 'user_data' not in context.chat_data:
            context.chat_data['user_data'] = {}
        if user_id not in context.chat_data['user_data']:
            context.chat_data['user_data'][user_id] = {}
        
        context.chat_data['user_data'][user_id]['menu_level'] = level
        
        # Display appropriate menu based on level
        if level == "main":
            await query.edit_message_reply_markup(reply_markup=build_main_menu(language))
        
        elif level == "chat_modes":
            # Update message text to explain chat modes
            await query.edit_message_text(
                get_text("chat_modes_explanation", language, 
                         default="Wybierz tryb czatu, którego chcesz użyć:"),
                reply_markup=build_chat_modes_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "notes":
            await query.edit_message_text(
                get_text("notes_menu_title", language, 
                         default="📝 *Menu Notatek*\n\nWybierz opcję:"),
                reply_markup=build_notes_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "reminders":
            await query.edit_message_text(
                get_text("reminders_menu_title", language, 
                         default="⏰ *Menu Przypomnień*\n\nWybierz opcję:"),
                reply_markup=build_reminders_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "credits":
            await query.edit_message_text(
                get_text("credits_menu_title", language, 
                         default="💰 *Menu Kredytów*\n\nZarządzaj swoimi kredytami:"),
                reply_markup=build_credits_menu(language, user_id),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "buy_credits":
            await query.edit_message_text(
                get_text("buy_credits_title", language, 
                         default="🛒 *Kup Kredyty*\n\nWybierz pakiet kredytów:"),
                reply_markup=build_buy_credits_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "account":
            await query.edit_message_text(
                get_text("account_menu_title", language, 
                         default="📊 *Menu Konta*\n\nZarządzaj swoim kontem:"),
                reply_markup=build_account_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "settings":
            await query.edit_message_text(
                get_text("settings_title", language),
                reply_markup=build_settings_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "language":
            await query.edit_message_text(
                get_text("settings_choose_language", language),
                reply_markup=build_language_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "model":
            await query.edit_message_text(
                get_text("settings_choose_model", language),
                reply_markup=build_model_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif level == "help":
            await query.edit_message_text(
                get_text("help_menu_title", language, 
                         default="❓ *Menu Pomocy*\n\nWybierz opcję:"),
                reply_markup=build_help_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
    
    #################################
    # Back navigation
    #################################
    
    # Handle back navigation
    elif callback_data.startswith("menu_back_to_"):
        target_level = callback_data[13:]  # Extract level name after "menu_back_to_"
        
        # Update user's menu state
        if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
            context.chat_data['user_data'][user_id]['menu_level'] = target_level
        
        # Navigate back to appropriate level
        if target_level == "main":
            # Reset to main menu with welcome message
            credits = get_user_credits(user_id)
            welcome_text = get_text("welcome_message", language, bot_name=BOT_NAME, credits=credits)
            
            await query.edit_message_text(
                welcome_text,
                reply_markup=build_main_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif target_level == "credits":
            await query.edit_message_text(
                get_text("credits_menu_title", language, 
                         default="💰 *Menu Kredytów*\n\nZarządzaj swoimi kredytami:"),
                reply_markup=build_credits_menu(language, user_id),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif target_level == "settings":
            await query.edit_message_text(
                get_text("settings_title", language),
                reply_markup=build_settings_menu(language),
                parse_mode=ParseMode.MARKDOWN
            )
    
    #################################
    # Actions
    #################################
    
    # Handle actions (performing specific tasks)
    elif callback_data.startswith("menu_action_"):
        action = callback_data[12:]  # Extract action name after "menu_action_"
        
        # Special case for dummy action that does nothing (used for display-only buttons)
        if action == "none":
            return
        
        # New chat action
        if action == "newchat":
            from handlers.chat_handler import new_chat
            await new_chat(update, context)
        
        # Notes actions
        elif action == "view_notes":
            from handlers.note_handler import notes_command
            await notes_command(update, context)
        
        elif action == "create_note":
            await query.edit_message_text(
                get_text("create_note_instructions", language, 
                         default="Aby utworzyć nową notatkę, użyj komendy:\n\n`/note [tytuł] [treść]`\n\nNa przykład:\n`/note Zakupy Mleko, chleb, jajka`"),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Reminders actions
        elif action == "view_reminders":
            from handlers.reminder_handler import reminders_command
            await reminders_command(update, context)
        
        elif action == "create_reminder":
            await query.edit_message_text(
                get_text("create_reminder_instructions", language, 
                         default="Aby utworzyć nowe przypomnienie, użyj komendy:\n\n`/remind [czas] [treść]`\n\nPrzykłady:\n`/remind 30m Zadzwonić do klienta`\n`/remind 2h Spotkanie`\n`/remind 18:00 Trening`"),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Credits actions
        elif action == "enter_code":
            await query.edit_message_text(
                get_text("enter_code_instructions", language, 
                         default="Aby aktywować kod promocyjny, użyj komendy:\n\n`/code [twój_kod]`\n\nNa przykład:\n`/code ABC123`"),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif action.startswith("buy_package_"):
            package_id = int(action.split("_")[2])
            
            # Here you would integrate with your payment system
            # For this example, just show confirmation message
            await query.edit_message_text(
                get_text("buy_package_instructions", language, 
                         default=f"Aby kupić pakiet kredytów, użyj komendy:\n\n`/buy {package_id}`"),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Account/settings actions
        elif action == "view_stats":
            from handlers.credit_handler import credit_stats_command
            await credit_stats_command(update, context)
        
        elif action == "export":
            from handlers.export_handler import export_conversation
            await export_conversation(update, context)
        
        elif action == "restart":
            from main import restart_command
            await restart_command(update, context)
        
        elif action == "set_name":
            await query.edit_message_text(
                get_text("settings_change_name", language),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Chat mode selection
        elif action.startswith("set_mode_"):
            mode_id = action[9:]  # Extract mode_id after "set_mode_"
            
            # Save selected mode
            if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id]['current_mode'] = mode_id
                
                # If mode has a specific model, set it too
                if "model" in CHAT_MODES[mode_id]:
                    context.chat_data['user_data'][user_id]['current_model'] = CHAT_MODES[mode_id]["model"]
            
            # Get mode info for confirmation message
            mode_name = CHAT_MODES[mode_id]["name"]
            if language == 'en' and 'name_en' in CHAT_MODES[mode_id]:
                mode_name = CHAT_MODES[mode_id]["name_en"]
            elif language == 'ru' and 'name_ru' in CHAT_MODES[mode_id]:
                mode_name = CHAT_MODES[mode_id]["name_ru"]
            
            credit_cost = CHAT_MODES[mode_id]["credit_cost"]
            
            # Show confirmation message
            await query.edit_message_text(
                get_text("mode_selected", language, 
                         default=f"Wybrany tryb: *{mode_name}*\nKoszt: *{credit_cost}* kredyt(ów) za wiadomość\n\nMożesz teraz zadać pytanie."),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Model selection
        elif action.startswith("set_model_"):
            model_id = action[10:]  # Extract model_id after "set_model_"
            
            # Save selected model
            if 'user_data' in context.chat_data and user_id in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id]['current_model'] = model_id
            
            # Show confirmation message
            from config import CREDIT_COSTS
            model_name = AVAILABLE_MODELS[model_id]
            credit_cost = CREDIT_COSTS["message"].get(model_id, CREDIT_COSTS["message"]["default"])
            
            await query.edit_message_text(
                get_text("model_selected", language, model=model_name, credits=credit_cost),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Language selection
        elif action.startswith("set_language_"):
            new_language = action[13:]  # Extract language code after "set_language_"
            
            # Save selected language
            if 'user_data' not in context.chat_data:
                context.chat_data['user_data'] = {}
            if user_id not in context.chat_data['user_data']:
                context.chat_data['user_data'][user_id] = {}
            
            context.chat_data['user_data'][user_id]['language'] = new_language
            
            # Update in database
            try:
                from database.sqlite_client import sqlite3, DB_PATH
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET selected_language = ? WHERE id = ?", 
                              (new_language, user_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Błąd zapisywania języka: {e}")
            
            # Get language name for confirmation
            language_name = AVAILABLE_LANGUAGES.get(new_language, new_language)
            
            # Show confirmation with restart button
            await query.edit_message_text(
                f"{get_text('language_selected', new_language, language_display=language_name)}\n\n"
                f"{get_text('restart_suggestion', new_language)}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        get_text("restart_button", new_language), 
                        callback_data="restart_bot"
                    )
                ]])
            )
        
        # Help actions
        elif action == "show_commands":
            commands_text = get_text("help_text", language)
            await query.edit_message_text(
                commands_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "🔙 " + get_text("back_button", language, default="Wstecz"), 
                        callback_data="menu_back_to_help"
                    )
                ]])
            )
        
        elif action == "faq":
            faq_text = get_text("faq_text", language, 
                                default="*Najczęściej zadawane pytania*\n\n"
                                "**Jak kupić kredyty?**\n"
                                "Użyj komendy /buy lub wybierz opcję w menu.\n\n"
                                "**Ile kosztują poszczególne operacje?**\n"
                                "- Standardowa wiadomość (GPT-3.5): 1 kredyt\n"
                                "- Wiadomość Premium (GPT-4o): 3 kredyty\n"
                                "- Wiadomość Ekspercka (GPT-4): 5 kredytów\n"
                                "- Obraz DALL-E: 10-15 kredytów\n"
                                "- Analiza dokumentu: 5 kredytów\n"
                                "- Analiza zdjęcia: 8 kredytów\n\n"
                                "**Jak zmienić język?**\n"
                                "Przejdź do Ustawienia -> Język w menu.")
            
            await query.edit_message_text(
                faq_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "🔙 " + get_text("back_button", language, default="Wstecz"), 
                        callback_data="menu_back_to_help"
                    )
                ]])
            )

# Add the extra translations needed for the menu system
def add_menu_translations():
    """Add necessary translations for the menu system to the translations module"""
    from utils.translations import translations
    
    # Polish translations
    translations["pl"]["back_button"] = "Wstecz"
    translations["pl"]["chat_modes_explanation"] = "Wybierz tryb czatu, którego chcesz użyć:"
    translations["pl"]["notes_menu_title"] = "📝 *Menu Notatek*\n\nWybierz opcję:"
    translations["pl"]["view_notes"] = "Zobacz notatki"
    translations["pl"]["create_note"] = "Utwórz notatkę"
    translations["pl"]["create_note_instructions"] = "Aby utworzyć nową notatkę, użyj komendy:\n\n`/note [tytuł] [treść]`\n\nNa przykład:\n`/note Zakupy Mleko, chleb, jajka`"
    translations["pl"]["reminders_menu_title"] = "⏰ *Menu Przypomnień*\n\nWybierz opcję:"
    translations["pl"]["view_reminders"] = "Zobacz przypomnienia"
    translations["pl"]["create_reminder"] = "Utwórz przypomnienie"
    translations["pl"]["create_reminder_instructions"] = "Aby utworzyć nowe przypomnienie, użyj komendy:\n\n`/remind [czas] [treść]`\n\nPrzykłady:\n`/remind 30m Zadzwonić do klienta`\n`/remind 2h Spotkanie`\n`/remind 18:00 Trening`"
    translations["pl"]["credits_menu_title"] = "💰 *Menu Kredytów*\n\nZarządzaj swoimi kredytami:"
    translations["pl"]["buy_credits_title"] = "🛒 *Kup Kredyty*\n\nWybierz pakiet kredytów:"
    translations["pl"]["balance"] = "Saldo"
    translations["pl"]["enter_code"] = "Wprowadź kod"
    translations["pl"]["enter_code_instructions"] = "Aby aktywować kod promocyjny, użyj komendy:\n\n`/code [twój_kod]`\n\nNa przykład:\n`/code ABC123`"
    translations["pl"]["buy_package_instructions"] = "Aby kupić pakiet kredytów, użyj komendy:\n\n`/buy {0}`"
    translations["pl"]["account_menu_title"] = "📊 *Menu Konta*\n\nZarządzaj swoim kontem:"
    translations["pl"]["view_stats"] = "Zobacz statystyki"
    translations["pl"]["export_conversation"] = "Eksportuj rozmowę"
    translations["pl"]["help_menu_title"] = "❓ *Menu Pomocy*\n\nWybierz opcję:"
    translations["pl"]["commands_list"] = "Lista komend"
    translations["pl"]["faq"] = "FAQ"
    translations["pl"]["faq_text"] = "*Najczęściej zadawane pytania*\n\n**Jak kupić kredyty?**\nUżyj komendy /buy lub wybierz opcję w menu.\n\n**Ile kosztują poszczególne operacje?**\n- Standardowa wiadomość (GPT-3.5): 1 kredyt\n- Wiadomość Premium (GPT-4o): 3 kredyty\n- Wiadomość Ekspercka (GPT-4): 5 kredytów\n- Obraz DALL-E: 10-15 kredytów\n- Analiza dokumentu: 5 kredytów\n- Analiza zdjęcia: 8 kredytów\n\n**Jak zmienić język?**\nPrzejdź do Ustawienia -> Język w menu."
    
    # English translations (add similar entries for "en")
    translations["en"]["back_button"] = "Back"
    translations["en"]["chat_modes_explanation"] = "Choose the chat mode you want to use:"
    # Add more English translations...
    
    # Russian translations (add similar entries for "ru")
    translations["ru"]["back_button"] = "Назад"
    translations["ru"]["chat_modes_explanation"] = "Выберите режим чата, который хотите использовать:"
    # Add more Russian translations...

# Call this function to add translations when the module is imported
add_menu_translations()