import pyautogui
from time import sleep

# --- Globals for default paths ---
_default_autopath = r'C:\\'
_default_altpath = None

def set_autopath(path):
    """Sets the global default primary path for images."""
    global _default_autopath
    _default_autopath = path

def set_altpath(path):
    """Sets the global default alternate path for images."""
    global _default_altpath
    _default_altpath = path

def optimiseWait(filename, dontwait=False, specreg=None, clicks=1, xoff=0, yoff=0, autopath=None, altpath=None, scrolltofind=None):
    """
    Waits for one of several images to appear on screen and clicks it.
    This version is robust against missing image files.
    """
    global _default_autopath, _default_altpath
    
    # --- Path Resolution ---
    # Use the provided autopath, otherwise fall back to the global default.
    autopath = autopath if autopath is not None else _default_autopath
    # Use the provided altpath, otherwise fall back to the global default.
    # Note: This logic assumes altpath=None is an explicit instruction not to use the default altpath.
    altpath = altpath if altpath is not None else _default_altpath
    
    # --- Parameter Normalization (ensuring single values become lists) ---
    if not isinstance(filename, list):
        filename = [filename]
    
    if not isinstance(clicks, list):
        clicks = [clicks] + [1] * (len(filename) - 1)
    elif len(clicks) < len(filename):
        clicks.extend([1] * (len(filename) - len(clicks)))
    
    if not isinstance(xoff, list):
        xoff = [xoff] * len(filename)
    elif len(xoff) < len(filename):
        xoff.extend([0] * (len(filename) - len(xoff)))
        
    if not isinstance(yoff, list):
        yoff = [yoff] * len(filename)
    elif len(yoff) < len(filename):
        yoff.extend([0] * (len(filename) - len(yoff)))

    # --- Main Loop ---
    while True:
        findloc = None
        clicked_index = -1 # Use a more descriptive name than 'clicked'
        
        # --- Image Search Loop ---
        for i, fname in enumerate(filename):
            # Try main path first
            try:
                img_path = fr'{autopath}\{fname}.png'
                if specreg is None:
                    loc = pyautogui.locateCenterOnScreen(img_path, confidence=0.9)
                else:
                    # locateOnScreen returns a Box(left, top, width, height)
                    loc = pyautogui.locateOnScreen(img_path, region=specreg, confidence=0.9)
                
                if loc:
                    findloc = loc
                    clicked_index = i
                    break # Exit the for loop since we found an image
            # --- MODIFIED LINE ---
            # Catch both when the image is not on screen AND when the file doesn't exist.
            except (pyautogui.ImageNotFoundException, FileNotFoundError):
                # This image was not found, so we continue to the next one in the list.
                pass 
            
            # Try alt path if provided and image wasn't found in main path
            if altpath is not None:
                try:
                    img_path_alt = fr'{altpath}\{fname}.png'
                    if specreg is None:
                        loc = pyautogui.locateCenterOnScreen(img_path_alt, confidence=0.9)
                    else:
                        loc = pyautogui.locateOnScreen(img_path_alt, region=specreg, confidence=0.9)
                    
                    if loc:
                        findloc = loc
                        clicked_index = i
                        break # Exit the for loop since we found an image
                # --- MODIFIED LINE ---
                # Also catch both exceptions for the alternate path.
                except (pyautogui.ImageNotFoundException, FileNotFoundError):
                    # This image was not found in the alt path, continue.
                    pass
        
        # --- Action Phase (Clicking) ---
        if findloc is not None:
            # If specreg is used, locateOnScreen gives a box, not a center point.
            # We need to calculate the center to apply offsets correctly.
            if specreg is None:
                x, y = findloc # Already a center point
            else:
                # findloc is a Box(left, top, width, height)
                # Calculate center point to apply offsets consistently
                x = findloc.left + findloc.width / 2
                y = findloc.top + findloc.height / 2
            
            current_xoff = xoff[clicked_index]
            current_yoff = yoff[clicked_index]
            click_count = clicks[clicked_index]
            
            x_to_click = x + current_xoff
            y_to_click = y + current_yoff
            
            sleep(0.5) # A smaller pre-click delay is often sufficient

            if click_count > 0:
                pyautogui.click(x=x_to_click, y=y_to_click, clicks=click_count, interval=0.1)

        # --- Loop Control and Return Logic ---
        if findloc: # An image was found and action was taken
            if dontwait:
                return {'found': True, 'image': filename[clicked_index]}
            else:
                # In "wait" mode, finding the image means our job is done.
                break # Exit the 'while True' loop
        else: # No image was found in this pass
            if dontwait:
                # In "don't wait" mode, if we didn't find it, we return immediately.
                return {'found': False, 'image': None}
            else:
                # In "wait" mode, if we didn't find it, we scroll or pause.
                if scrolltofind == 'pageup':
                    pyautogui.press('pageup')
                    sleep(0.5)
                elif scrolltofind == 'pagedown':
                    pyautogui.press('pagedown')
                    sleep(0.5)
                else:
                    # Pause before the next search attempt if not scrolling
                    sleep(1)

    # This return is only reached when dontwait=False and the loop was broken (image found)
    return {'found': True, 'image': filename[clicked_index]}