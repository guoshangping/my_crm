from django.test import TestCase

# Create your tests here.
import re




ret=re.search("^/mysky/app01/order/$","/mysky/app01/order/1/change")
print(ret)

