import requests
from bs4 import BeautifulSoup

class PriceGold:
    def __init__(self, url):
        self.description = 'To get the latest price of gold in Indonesia from lakuemas.com'
        self.result = None
        self.url = url
    def data_extraction(self):
        try:
            content = requests.get(self.url)
        except Exception:
            return None
        if content.status_code == 200:
            soup = BeautifulSoup(content.text,'html.parser')
            results = soup.find('small', {'style': 'letter-spacing: 1px !important; font-size: 14px;'}) # find date and time
            results = results.text.split(',')
            prices_daily_at = results[2]
            update_gold_today = results[1]

            results = soup.find(    'h3', {'class':'font-weight-bold'}) # find buy price
            results = results.text
            buy_price = results

            results = soup.find('p',{'class':'font-weight-normal'}) # find weight
            results = results.text
            weight1 = results


            results = soup.find('div',{'class':'col-md-6 text-center border-left'})
            results = results.find_all()
            i = 0
            sell_price = None
            weight2 = None
            for res in results:
                if i == 1:
                    sell_price = res.text
                elif i == 2:
                    weight2 = res.text
                i = i + 1


            r = dict()
            r['update gold today'] = update_gold_today
            r['prices are update daily at'] = prices_daily_at
            r['buy price IDR'] = buy_price
            r['weight buy'] = weight1
            r['sell price'] = sell_price
            r['weight sell'] = weight2
            self.result = r
        else:
            return None

    def view_data(self):
        if self.result is None:
            print('Data not found!')
            return
        print('Update Price Gold Today source lakuemas.com')
        print('\n')
        print(f"Update gold today{self.result['update gold today']}")
        print(f"Prices are update daily at{self.result['prices are update daily at']}")
        print(f"Buy price {self.result['buy price IDR']}")
        print(f"Weight : {self.result['weight buy']}")
        print(f"Sell price {self.result['sell price']}")
        print(f"Weight : {self.result['weight sell']}")

    def run(self):
        self.data_extraction()
        self.view_data()

if __name__ == '__main__':
    update_gold_Indonesia = PriceGold('https://www.lakuemas.com')
    print('Class description PriceGold',update_gold_Indonesia.description)
    update_gold_Indonesia.run()