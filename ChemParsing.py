# A simple routine using pyparsing to identify chemical names, amounts, and a set of defined
# roles and return these as a dictionary to the calling function.

from pyparsing import *

units = oneOf('g mg ugl ml ul L mL uL').setResultsName('units')
role = oneOf('startingmaterial solvent reagent product').setResultsName('role') 
chemicalname = Regex('[a-zA-Z0-9-]{1,20}').setResultsName('chemicalname')
amount = Regex('\\s?(\\d{0,5}\\.?\\d{0,5})?').setResultsName('amount')
quantity = amount + units

chemstring = chemicalname + (Optional(quantity) & Optional(role))

def chemparse(text):
    """Accept a text string and parse, return the results as a dictionary"""

    results = chemstring.parseString(text)
    dict = {'name'  : results.chemicalname,
            'amount': results.amount,
            'units' : results.units,
            'role'  : results.role}

    return dict

    

# some hacked together tests
if __name__ == '__main__':
  tests = [ "benzene", 
          "glucose 5g", 
          "acetone 5 ml", 
          "benzene solvent image", 
          "glucose 5g startingmaterial", 
          "2-5-dithioglucose 7.34mg product"]

  for t in tests:
    try:
        results = chemstring.parseString(t)
        dict = {'name': results.chemicalname,
                'amount':results.amount,
                'units':results.units,
                'role':results.role}
        print dict
        print t, results
    except ParseException, pe:
        print pe
