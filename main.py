from playwright.sync_api import sync_playwright
from dataclasses import dataclass, field, asdict
import pandas as pd
import argparse

@dataclass
class Business:
    name: str = None
    address: str = None
    phone: str = None
    website: str = None
    
@dataclass
class BusinessList:
    businesses: list[Business] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.json_normalize((asdict(business) for business in self.businesses), sep='_')
    
    def save_to_excel(self, filename: str) -> None:
        self.to_dataframe().to_excel(f'{filename}.xlsx', index=False, engine='openpyxl')
    
    def save_to_csv(self, filename: str) -> None:
        self.to_dataframe().to_csv(f'{filename}.csv', index=False, encoding='utf-8')

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto('https://www.google.com/maps', timeout=60000)
        page.wait_for_timeout(5000)
        
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(3000)
        
        page.keyboard.press('Enter')
        page.wait_for_timeout(5000)
        
        listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
        print(len(listings))
        
        businesses = BusinessList()
        
        for listing in listings[:5]:
            listing.click()
            page.wait_for_timeout(5000)
            
            name_attibute = 'aria-label'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
  
            business = Business()
            if len(listing.get_attribute(name_attibute)) >= 1:
        
                business.name = listing.get_attribute(name_attibute)
            else:
                business.name = ""
                
            if page.locator(address_xpath).count() > 0:
                business.address = page.locator(address_xpath).all()[0].inner_text()
            else:
                business.address = ""
                
            if page.locator(website_xpath).count() > 0:
                business.website = page.locator(website_xpath).all()[0].inner_text()
            else:
                business.website = ""
                
            if page.locator(phone_number_xpath).count() > 0:
                business.phone = page.locator(phone_number_xpath).all()[0].inner_text()
            else:
                business.phone = ""
            
            businesses.businesses.append(business)
        
        businesses.save_to_excel('googole_maps_data')
        businesses.save_to_csv('googole_maps_data')
        
        browser.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web scraping script.')
    parser.add_argument("-s", "--search", type=str, required=True, help='URL to scrape')
    parser.add_argument("-l", '--location', type=str, required=True, help='Output file name (with .xlsx or .csv)')
    args = parser.parse_args()

    if args.location and args.search:
        search_for = f'{args.search}  {args.location}'
    else :
        search_for = 'dentist new york'
        
    main()    
   