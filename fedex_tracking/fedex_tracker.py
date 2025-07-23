import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException

def fedex_track(tracking_number):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)

    try:
        print("🔄 Opening FedEx tracking page...")
        driver.get("https://www.fedex.com/en-in/tracking.html")

        print("⏳ Waiting for input field...")
        input_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[id^='tracking_number_']"))
        )
        print("✅ Input field found.")

        input_box.clear()
        for char in tracking_number:
            input_box.send_keys(char)
            time.sleep(0.1)

        # Close GDPR popup if visible
        try:
            gdpr_reject_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".fxg-gdpr__reject-all-btn"))
            )
            print("⚠️ GDPR popup detected. Closing it...")
            gdpr_reject_button.click()
            time.sleep(1)
        except:
            print("No GDPR popup detected. Continuing...")

        print("🔘 Looking for Track button...")
        track_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].fdx-c-button--primary"))
        )
        print("✅ Track button found. Clicking...")
        track_button.click()

        print("🚚 Tracking number submitted!")
        WebDriverWait(driver, 30).until(EC.title_contains("Detailed Tracking"))

        print("⏳ Waiting for delivery information to load...")

        # Extract tracking info
        status_main = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-test-id='delivery-date-header']"))
        ).text.strip()
        if "DELIVERED" in status_main.upper():
            status_main = "Delivered"
        elif "NOT" in status_main.upper():
            status_main = "Not Delivered"

        delivery_day = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.deliveryDateText"))
        ).text.strip()

        delivery_datetime = driver.execute_script("""
            let el = document.querySelector("span.deliveryDateTextBetween");
            return el ? el.textContent.trim() : "Not Found";
        """)

        status_detailed = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.fdx-c-heading.fdx-c-heading--h5"))
        ).text.strip()

        # Display summary
        print("\n📦 **FedEx Tracking Summary**")
        print(f"Main Delivery Status   : {status_main}")
        print(f"Delivery Day           : {delivery_day}")
        print(f"Delivery Date & Time   : {delivery_datetime}")
        print(f"Delivery Status Detail : {status_detailed}")

        input("\n🔍 PRESS ENTER TO KNOW MORE DETAILED DELIVERY HISTORY...")

        print("🧭 Clicking 'View travel history'...")
        view_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'View travel history')]"))
        )
        view_button.click()
        time.sleep(2)

        print("⏳ Extracting detailed travel history...")

        travel_history = driver.execute_script("""
        const host = document.querySelector('fx-tracking-result');
        if (!host || !host.shadowRoot) return 'No shadow root found';

        const events = host.shadowRoot.querySelectorAll('.travel-history-card');
        let history = [];

        events.forEach(card => {
            let date = card.querySelector('.travel-history-card-date')?.innerText.trim() || '';
            let subEvents = card.querySelectorAll('.travel-history-card-event');
            subEvents.forEach(event => {
                let time = event.querySelector('.travel-history-event-time')?.innerText.trim() || '';
                let status = event.querySelector('.travel-history-event-status')?.innerText.trim() || '';
                let location = event.querySelector('.travel-history-event-location')?.innerText.trim() || '';
                history.push(`${date}\\n${time} — ${status}${location ? ' @ ' + location : ''}`);
            });
        });

        return history.join('\\n\\n');
        """)

        print("\n📜 **Detailed Travel History**\n")
        print(travel_history)

        input("\n🔚 PRESS ESC TO EXIT (or close window manually)...")

    except TimeoutException as e:
        print("❌ Timeout waiting for page elements:", str(e))
    except Exception as e:
        print("❌ Unexpected error:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    tracking_num = "881618932162"  # 🔁 Replace with any other tracking number if needed
    fedex_track(tracking_num)
