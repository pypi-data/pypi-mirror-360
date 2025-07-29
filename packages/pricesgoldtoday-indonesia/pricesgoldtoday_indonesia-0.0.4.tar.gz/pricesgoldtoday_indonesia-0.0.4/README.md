# price-gold-today-id
This package will get update price gold in Indonesia, source from lakuemas.com

## HOW IT'S WORK?
this package will scrape from [Lakuemas](https://www.lakuemas.com/) to get update price gold /gram. This price is IDR!
this package will use BeautifulSoup4 and requests, to produce output in the form of JSON that is ready to be used
in web or mobile applications.

# How you can use! write in your pyhton 

```
from gold_today import PriceGold

if __name__ == '__main__':
    update_gold_Indonesia = PriceGold('https://www.lakuemas.com')
    print('Class description PriceGold',update_gold_Indonesia.description)
    update_gold_Indonesia.run()
```

# FOLLOW US!
[Linkedln Haeder Ali](https://www.linkedin.com/in/haederali/)