import time
import utils.constants as constants
import core.config as config
import core.bot as bot
from utils.log import info, warning, debug, error
from utils.tools import sleep, get_secs
import utils.device_action_wrapper as device_action

def handle_career_completion():
    info("Indikator 'Complete Career' terdeteksi. Memulai prosedur penyelesaian...")

    endtime = time.time() + 180  # Extended timeout as fallback
    has_bought_skills = False
    
    while time.time() < endtime:
        if not bot.is_bot_running:
            return 

        # Exit Condition: Deteksi tombol Auto Career (berarti sudah berada di Lobby kembali)
        if device_action.locate("assets/buttons/auto_career_btn.png", confidence=0.8, min_search_time=get_secs(0.5)):
            info("Terdeteksi Game Lobby (auto_career_btn). Prosedur penyelesaian Career tuntas!")
            return True

        # 0. Check and Buy Skills before Complete Career (if button exists)
        if not has_bought_skills and device_action.locate("assets/buttons/skills2_btn.png", confidence=0.8, min_search_time=0):
            info("Found skills button on career completion end screen. Buying skills first...")
            from core.skill import buy_skill_end_career
            buy_skill_end_career()
            has_bought_skills = True
            sleep(1)
            continue

        # 1. Check Complete Career (Header)
        if device_action.locate_and_click("assets/complete_career.png", confidence=0.8, min_search_time=get_secs(1)):
            sleep(1)
            continue
        
        # 2. Check Finish Button
        if device_action.locate_and_click("assets/buttons/finish_btn.png", confidence=0.8, min_search_time=get_secs(1)):
            sleep(1)
            continue
        
        # 3. Check Next Button
        if device_action.locate_and_click("assets/buttons/next_btn.png", confidence=0.8, min_search_time=get_secs(1)):
            sleep(1)
            continue
        
        # 4. Check Next 2 Button
        if device_action.locate_and_click("assets/buttons/next2_btn.png", confidence=0.8, min_search_time=get_secs(1)):
            sleep(1)
            continue

        # 5. Check Close Button
        if device_action.locate_and_click("assets/buttons/close_btn.png", confidence=0.8, min_search_time=get_secs(1)):
            sleep(1)
            continue

        # 6. Click random area to skip text if no buttons found
        # prioritize identifying known buttons over random clicks to avoid accidental selections
        # but if we are stuck, we might need to click.
        # Let's try to be less aggressive with random clicks in the new version unless necessary.
        # For now, keeping it as a fallback but with a check for other UI elements if possible.
        # implementation wise, the user's logic seems fine for skipping end-of-run dialogue.
        
        info("No buttons found, clicking random area to skip text.")
        # Attempt to click "TAP" area again just in case
        device_action.click(target=(constants.SCREEN_BOTTOM_REGION[0] + 100, constants.SCREEN_BOTTOM_REGION[1] + 100))
        sleep(1)
        continue

    info("Career completion check finished (Loop Timeout/Selesai).")
    return True 

def auto_start_career():
    info("Memeriksa status untuk Auto Start Career...")
    
    # 1. Check if we are already in-game (Training/Race screen)
    # Check for Tazuna hint
    if device_action.locate("assets/ui/tazuna_hint.png", min_search_time=get_secs(1)):
        info("Terdeteksi sudah berada di dalam Career (In-Game). Melanjutkan ke loop utama.")
        return True

    # 2. Check if we are at Support Card Selection
    if device_action.locate("assets/buttons/friends_support_icon.png", min_search_time=get_secs(1)):
        info("Terdeteksi di layar Support Card Selection.")
        auto_select_support_card()
        career_prep()
        return True

    # 3. Check if we are at Start Career Confirmation
    if device_action.locate("assets/buttons/start_career_btn.png", min_search_time=get_secs(1)):
        info("Terdeteksi di layar Start Career Confirmation.")
        career_prep()
        return True

    # 4. Check for New Game / Resume buttons (Standard Flow)
    if device_action.locate("assets/buttons/auto_career_btn.png", confidence=0.8, min_search_time=get_secs(1)):
        info("Tombol Auto Career ditemukan. Memulai sesi baru.")
        device_action.locate_and_click("assets/buttons/auto_career_btn.png")
        sleep(5)
    elif device_action.locate("assets/buttons/career_resume.png", min_search_time=get_secs(1)):
         info("Tombol Resume Career ditemukan.")
         device_action.locate_and_click("assets/buttons/career_resume.png")
         sleep(1)
         device_action.locate_and_click("assets/buttons/resume_btn.png", min_search_time=get_secs(5))
         sleep(5)
         return True
    elif device_action.locate("assets/buttons/resume_btn.png", min_search_time=get_secs(1)):
        info("Tombol Resume ditemukan langsung.")
        device_action.locate_and_click("assets/buttons/resume_btn.png")
        sleep(5)
        return True
    else:
        warning("Tidak menemukan indikator posisi yang dikenal. Mencoba masuk ke loop utama dan berharap bot bisa mengenali situasi.")
        return True
             
    # If we clicked Auto Career, we wait for the next screen (Support Card or Scenario Select)
    # Assuming Support Card selection is next for "Auto Career" flow or user handles scenario select manually if not skipped.
    endtime = time.time() + 30 
    
    while time.time() < endtime:
        if not bot.is_bot_running:
            return

        if handle_connection_error():
            continue

        if device_action.locate_and_click("assets/buttons/next_btn.png", min_search_time=get_secs(1)):
            sleep(1)
            continue

        # Verify if we are at support card selection
        if device_action.locate("assets/buttons/friends_support_icon.png", min_search_time=get_secs(1)):
             auto_select_support_card()
             sleep(1)
             career_prep() # Start the run
             sleep(1)
             return True
             
    info("Auto start sequence timeout. Melanjutkan ke loop utama.")
    return True

def auto_select_support_card():
    info("Memilih Support Card...")
    card_found = False
    # Use config for target cards if possible, otherwise default to a reasonable set
    target_cards = config.TARGET_SUPPORT_CARDS if hasattr(config, 'TARGET_SUPPORT_CARDS') else [
        "assets/cards/fuku.png"
    ]
    
    # Click friend support icon to open list (if not already open, but usually this is part of the flow)
    # The user code clicked "assets/buttons/friends_support_icon.png".
    # We should ensure we are on the selection screen.
    
    device_action.locate_and_click("assets/buttons/friends_support_icon.png", min_search_time=get_secs(3))
    sleep(1)

    refresh_count = 0
    while True:
        if not bot.is_bot_running: 
            return
        
        for scroll_count in range(3):
            for card_img in target_cards:
                if device_action.locate_and_click(card_img, confidence=0.8):
                    card_found = True
                    break
            
            if card_found:
                break
            
            # Scroll down
            scroll_start_pos = (829, 617) # This might need adjustment based on resolution/device
            # Using relative scroll if possible is safer, but hardcoded coords work for specific res
            device_action.swipe(scroll_start_pos, (scroll_start_pos[0], scroll_start_pos[1] - 417), duration=0.5)
            sleep(1.5)
        
        if card_found:
            break
            
        refresh_count += 1
        info(f"Card tidak ketemu. Melakukan Refresh ({refresh_count})...")
        if device_action.locate_and_click("assets/buttons/refresh_btn.png", min_search_time=get_secs(2)):
            sleep(1)
            # Handle confirm refresh if needed? Usually there is a confirmation dialog.
            device_action.locate_and_click("assets/buttons/ok_btn.png", min_search_time=get_secs(2))
        else:
            warning("Tombol Refresh tidak ditemukan. Mencoba scroll lagi...")

def career_prep():
    info("Mencoba Start Career...")
    
    device_action.locate_and_click("assets/buttons/start_career_btn.png", min_search_time=get_secs(3))
    sleep(1)
    
    # TP Restore Logic
    if device_action.locate("assets/buttons/restore_btn.png", confidence=0.8, min_search_time=get_secs(1)):
        info("TP Kurang! Melakukan Restore TP...")
        
        device_action.locate_and_click("assets/buttons/restore_btn.png")
        sleep(1)
        
        device_action.click(target=(764, 271))
        sleep(0.5)
        
        # Max out TP usage? User code clicked plus_btn twice.
        for _ in range(2):
            device_action.locate_and_click("assets/buttons/plus_btn.png")
        sleep(0.5)
        
        device_action.locate_and_click("assets/buttons/ok_btn.png")
        sleep(1)
        
        device_action.locate_and_click("assets/buttons/close_btn.png")
        sleep(1)
        
        device_action.locate_and_click("assets/buttons/start_career_btn.png", min_search_time=get_secs(3))
        # Confirmation for start?
        device_action.locate_and_click("assets/buttons/start_career_btn.png", min_search_time=get_secs(3))

    # Final Start Button Click
    device_action.locate_and_click("assets/buttons/start_career_btn.png", min_search_time=get_secs(3))
    sleep(5)
    
    info("Melewati Intro...")
    
    device_action.locate_and_click("assets/buttons/skip_btn.png", region_ltrb=constants.SCREEN_BOTTOM_BBOX, min_search_time=get_secs(10))
    sleep(1)
    
    # User had skip settings logic here
    device_action.locate_and_click("assets/buttons/skip_off.png")
    sleep(0.2)
    device_action.locate_and_click("assets/buttons/skip_x1.png")
    sleep(0.5)
    
    device_action.locate_and_click("assets/buttons/confirm_btn.png")
    
    info("Auto Career Setup Selesai. Masuk ke Career Lobby.")
    return True

def handle_connection_error():
    """
    Handles connection error popup.
    Retries clicking 'Retry' or 'OK' button. If fails, clicks 'Title Screen'.
    If all fails, clicks a generic fallback location to dismiss the modal.
    Returns True if connection error was detected and handled, False otherwise.
    """
    # Check for connection error popup
    if not device_action.locate("assets/connection_error.png", confidence=0.8, min_search_time=0):
        return False
    
    info("Connection Error detected!")
    
    # Try Retry or OK button
    retry_count = 0
    while retry_count < 3:
        if device_action.locate_and_click("assets/buttons/retry_btn.png", min_search_time=get_secs(1)) or \
           device_action.locate_and_click("assets/buttons/ok_btn.png", min_search_time=get_secs(0.5)) or \
           device_action.locate_and_click("assets/buttons/ok_2_btn.png", min_search_time=get_secs(0.5)):
            info(f"Clicked Retry/OK button ({retry_count+1}).")
            sleep(5) 
            if not device_action.locate("assets/connection_error.png", confidence=0.8, min_search_time=1):
                info("Reconnected successfully.")
                return True
            retry_count += 1
        else:
            break
            
    # If Retry button not found or error persists after retries, try Title Screen
    warning("Retry/OK failed or not found. Attempting Title Screen.")
    if device_action.locate_and_click("assets/buttons/title_screen_btn.png", min_search_time=get_secs(1)):
        info("Clicked Title Screen button.")
        sleep(10) # Initial wait
        process_title_screen()
        return True
    
    # Error was detected but known buttons weren't found. Let's do a fallback click.
    warning("Failed to find known buttons. Attempting fallback click to clear modal.")
    gw_x, gw_y, gw_w, gw_h = constants.GAME_WINDOW_REGION
    fallback_x = gw_x + (gw_w // 2)
    fallback_y = gw_y + int(gw_h * 0.65) # standard button height relative to game window
    device_action.click(target=(fallback_x, fallback_y), text="Connection Error Fallback Click")
    sleep(3)
    
    # Re-check if it's gone
    if not device_action.locate("assets/connection_error.png", confidence=0.8, min_search_time=0.5):
        info("Fallback click cleared the connection error.")
        return True

    warning("Error persists after fallback click.")
    return True  # Still return True because an error screen is actively blocking us

def process_title_screen():
    """
    Handles the Title Screen -> Game Lobby transition.
    Wait for loading -> Click "Tap to Start" -> Wait for loading -> Check for error recursively -> Go to Game Lobby.
    """
    info("Processing Title Screen...")
    
    # Click center 3x (Tap to Start) - user requested ensure mechanism
    gw_x, gw_y, gw_w, gw_h = constants.GAME_WINDOW_REGION
    center_x = gw_x + (gw_w // 2)
    center_y = gw_y + (gw_h // 2)
    
    info("Tapping center (Tap to Start)...")
    for i in range(3):
        device_action.click(target=(center_x, center_y))
        sleep(1)
        
    info("Waiting for loading after Title Screen...")
    
    timeout = time.time() + 120 # 2 minute max wait for full load
    while time.time() < timeout:
        if not bot.is_bot_running: return

        # Check for recurring connection error
        if device_action.locate("assets/connection_error.png", confidence=0.8, min_search_time=0.5):
             warning("Connection Error occurred during Title Screen loading!")
             handle_connection_error() # Recurse
             return
             
        # Check if we are in Game Lobby
        if device_action.locate("assets/buttons/auto_career_btn.png", confidence=0.8, min_search_time=0.5) or \
           device_action.locate("assets/buttons/career_resume.png", confidence=0.8, min_search_time=0.5) or \
           device_action.locate("assets/buttons/resume_btn.png", confidence=0.8, min_search_time=0.5):
             info("Game Lobby detected.")
             process_game_lobby()
             return

        # Check for Date Changed
        handle_date_changed()

        sleep(1)
        
    warning("Timeout waiting for Game Lobby after Title Screen.")

def process_game_lobby():
    """
    Handles Game Lobby actions:
    - Career Resume -> Resume
    - Auto Career -> Auto Start
    """
    info("Processing Game Lobby actions...")
    
    # Check for Career Resume
    if device_action.locate("assets/buttons/career_resume.png", min_search_time=get_secs(1)) or \
       device_action.locate("assets/buttons/resume_btn.png", min_search_time=get_secs(1)):
         
         if device_action.locate_and_click("assets/buttons/career_resume.png"):
             sleep(1)
             
         info("Resuming Career...")
         device_action.locate_and_click("assets/buttons/resume_btn.png", min_search_time=get_secs(5))
         
         # Wait for Tazuna (In-game)
         info("Waiting for In-Game (Tazuna)...")
         timeout = time.time() + 60
         while time.time() < timeout:
             if device_action.locate("assets/ui/tazuna_hint.png", min_search_time=0.5) or \
                device_action.locate("assets/buttons/details_btn.png", region_ltrb=constants.SCREEN_TOP_BBOX, min_search_time=0.5):
                 info("Resumed successfully.")
                 return
             sleep(1)
         warning("Timed out waiting for resume.")
         return

    # Check for Auto Career
    if device_action.locate("assets/buttons/auto_career_btn.png", min_search_time=get_secs(2)):
         info("Auto Career found. Starting Auto Start Career lifecycle...")
         auto_start_career()
         return

def check_game_lobby():
    """
    Checks if game lobby is visible (Auto Career or Resume buttons).
    Returns True if detected, False otherwise.
    """
    if device_action.locate("assets/buttons/auto_career_btn.png", confidence=0.8, min_search_time=0) or \
       device_action.locate("assets/buttons/career_resume.png", confidence=0.8, min_search_time=0):
        info("Game Lobby terdeteksi secara proaktif!")
        return True
    return False

def check_career_completion():
    """
    Checks if career completion screen is visible.
    Returns True if detected, False otherwise.
    This allows proactive detection instead of waiting for stuck condition.
    """
    if device_action.locate("assets/complete_career.png", confidence=0.8, min_search_time=0) or \
       device_action.locate("assets/buttons/complete_career_btn.png", confidence=0.8, min_search_time=0):
        info("Career Completion detected proactively!")
        return True
    return False

def handle_date_changed():
    """
    Handles 'Date Changed' popup.
    Click OK -> Wait Loading -> Click Skip (if any) -> Go to Game Lobby.
    Returns True if date changed popup was detected and handled, False otherwise.
    """
    if not device_action.locate("assets/date_changed.png", confidence=0.8, min_search_time=0):
        return False
    
    info("Date Changed popup detected!")
    
    if device_action.locate_and_click("assets/buttons/ok_btn.png", min_search_time=get_secs(2)):
        info("Clicked OK on Date Changed.")
    
    info("Waiting for loading after Date Changed...")
    sleep(5)
    
    # Check for Skip button or Lobby
    timeout = time.time() + 60
    while time.time() < timeout:
         if device_action.locate_and_click("assets/buttons/skip_btn.png", min_search_time=0.5):
             info("Clicked Skip.")
             sleep(1)
             continue
             
         # Check if we reached Lobby
         if device_action.locate("assets/buttons/auto_career_btn.png", confidence=0.8, min_search_time=0.5) or \
            device_action.locate("assets/buttons/career_resume.png", confidence=0.8, min_search_time=0.5):
             info("Game Lobby detected after Date Changed.")
             process_game_lobby()
             return True
             
         sleep(1)
    
    info("Date changed handling completed.")
    return True

