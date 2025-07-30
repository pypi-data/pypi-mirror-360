**\__’rithmetic__**

“rithmetic” is a budding python library which aims to provide arithmetic and math assistance to students using python to build math related functionality or apps.

**How to Install:**

Run the following command in Terminal/CLI –

- pip install rithmetic

If you are updating to a new version of rithmetic:

- pip install rithmetic --force-reinstall

After installation completes, run the following command in Terminal/CLI to see the welcome message –

- rith

To check the version of rithmetic, run the following command in Terminal/CLI –

- rith-version

**License and terms of use:**

rithmetic comes with the MIT license which means that anyone, anywhere can use it for any open source or even closed source application.

**Current functionality:**

1. Convert a number from one base to another (Converters)
2. Check/Verify if a number is from a specified base (Verifiers)
3. Add, Subtract, Multiply and Divide any two numbers in desired base (Operators)
4. Evaluate expressions with multiple arithmetic operations in desired base (Calculators)

**Best way to import:**

Import all the functions from rithmetic at once

from rithmetic import \*

**Functions:**

Converters

**base(num, fromB, toB)**

Converts any number from one base to another. (supported bases are base-2 to base-16)

num – any number | can be **int** or **float** or **str** type

fromB – base of ‘num’ | can be both **int** and **str** type

toB – ‘num’ gets converted to this base | can be both **int** and **str** type

Returns – The converted number in **int** or **str** or **float** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>number = base(1111,2,16)  
print(number)

This will print ‘F’. As 1111 in binary gets converted to F in hexadecimal.

**dectosub(num, toB)**

Converts any number from Decimal to any other sub-decimal base. (supported bases are base-2 to base-9)

num – any number | can be **int** or **float** or **str** type

toB – ‘num’ gets converted to this base | can be both **int** and **str** type

Returns – The converted number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>number = dectosub(23,5)  
print(number)

This will print 43. As 23 in decimal gets converted to 43 in base-5.

**subtodec(num, fromB)**

Converts any number from any sub-decimal base to Decimal. (supported bases are base-2 to base-9)

num – any number | can be **int** or **float** or **str** type

fromB – base of ‘num’ | can be both **int** and **str** type

Returns – The converted number in **int** or **float** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>number = subtodec(25,6)  
print(number)

This will print 17. As 25 in base-6 gets converted to 17 in decimal.

Quick single parameter converters

- **_Decimal to another base:_**

**dectob2(num)**

**dectob3(num)**

**dectob4(num)**

**dectob5(num)**

**dectob6(num)**

**dectob7(num)**

**dectob8(num)**

**dectob9(num)**

**dectob11(num)**

**dectob12(num)**

**dectob13(num)**

**dectob14(num)**

**dectob15(num)**

**dectob16(num)**

num – any number | can be **int** or **float** or **str** type

Return – The converted number in **int** or **str** type OR ‘Invalid number’

- **_Any base to Decimal_**

**b2todec(num)**

**b3todec(num)**

**b4todec(num)**

**b5todec(num)**

**b6todec(num)**

**b7todec(num)**

**b8todec(num)**

**b9todec(num)**

**b11todec(num)**

**b12todec(num)**

**b13todec(num)**

**b14todec(num)**

**b15todec(num)**

**b16todec(num)**

num – any number | can be **int** or **float** or **str** type

Return – The converted number in **int** or **float** type OR ‘Invalid number’

Verifiers

**chkbase(num, base)**

Checks if a number is from a specified base. (supported bases are base-2 to base-16)

num – any number | can be **int** or **float** or **str** type

base – base of ‘num’ to be checked | can be both **int** and **str** type

Returns – True OR False OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>check = chkbase('23F',16)  
print(check)

This will print True. As 23F is from base-16.

Quick single parameter verifiers

**chk2(num)**

**chk3(num)**

**chk4(num)**

**chk5(num)**

**chk6(num)**

**chk7(num)**

**chk8(num)**

**chk9(num)**

**chk10(num)**

**chk11(num)**

**chk12(num)**

**chk13(num)**

**chk14(num)**

**chk15(num)**

**chk16(num)**

num – any number | can be **int** or **float** or **str** type

Return – True OR False OR ‘Invalid number’

Operators

**add(num1, num2, Base)**

Adds two numbers in desired base. (supported bases are base-2 to base-16)

num1 – any number | can be **int** or **float** or **str** type

num2 – any number, which will be added to ‘num1’ | can be **int** or **float** or **str** type

Base– base of num1 and num2 | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>sum = add('2a',12,11)  
print(sum)

This will print 41. As (2a + 12) in base-11 is 41.

**sub(num1, num2, Base)**

Subtracts one number from another in desired base. (supported bases are base-2 to base-16)

num1 – any number | can be **int** or **float** or **str** type

num2 – any number, which will be subtracted from ‘num1’ | can be **int** or **float** or **str** type

Base– base of num1 and num2 | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>diff = sub(23,'6e',16)  
print(diff)

This will print -4B. As (23 – 6E) in base-16 is -4B.

**mul(num1, num2, Base)**

Multiplies two numbers in desired base. (supported bases are base-2 to base-16)

num1 – any number | can be **int** or **float** or **str** type

num2 – any number, which will be multiplied with ‘num1’ | can be **int** or **float** or **str** type

Base– base of num1 and num2 | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>prod = mul(12,24,11)  
print(prod)

This will print 288. As (12 \* 24) in base-11 is 288.

**div(num1, num2, Base)**

Divides a number by another in desired base. (supported bases are base-2 to base-16)

num1 – any number | can be **int** or **float** or **str** type

num2 – any number, ‘num1’ will be divided by this | can be **int** or **float** or **str** type

Base– base of num1 and num2 | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’ OR ‘Cannot divide by zero’

Example:

from rithmetic import \*  
<br/>quo = div(22,13,13)  
print(quo)

This will print 1.99999999999999. AS (22 / 13) in base-13 is 1.99999999999999

**addmany(\*nums, Base)**

Adds multiple numbers together in desired base. (supported bases are base-2 to base-16)

\*nums – a list or stream of numbers to be added together | can be **int** or **float** or **str** type

Base– base of \*nums | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>nums = \[12, 11, 14, 15, 12\]  
res = addmany(\*nums, Base=6)  
print(res)

This will print 112. As sum of the numbers in the list ‘nums’ is 112 in base-6

**mulmany(\*nums, Base)**

Multiplies multiple numbers together in desired base. (supported bases are base-2 to base-16)

\*nums – a list or stream of numbers to be multiplied together | can be **int** or **float** or **str** type

Base– base of \*nums | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’

Example:

from rithmetic import \*  
<br/>nums = \[1.2, 1.1, 1.4, 1.5, 1.2\]  
res = mulmany(\*nums, Base=6)  
print(res)

This will print 10.200515555555555555524. As product of the numbers in the list ‘nums’ is 10.200515555555555555524 in base-6

**power(num1, num2, Base)**

Calculates the exponent result of two numbers in desired base. (supported bases are base-2 to base-16)

num1 – any number | can be **int** or **float** or **str** type

num2 – any integer, which will be the power of ‘num1’ | can be **int** or **float** or **str** type

Base– base of num1 and num2 | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’ OR ‘Undefined’

Example:

from rithmetic import \*  
<br/>res = power(12,2,10)  
print(res)

This will print 144. As 12 to the power of 2 is 144 in base-10.

Calculators

**exp(expression, Base)**

Parses through a string expression and calculates it’s result in desired base. (supported bases are base-2 to base-16)

expression – any arithmetical expression | should be **str** type

Base– base of calculation and numbers in the expression | can be both **int** and **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’ OR ‘Invalid brackets’ OR ‘Undefined power operation’ OR ‘Cannot divide by zero’ OR ‘Operator missing operand’ OR ‘Invalid operators’ OR ‘Empty brackets’ OR ‘Brackets without any number’

Example:

from rithmetic import \*  
<br/>res = exp('((101+101)11-10)/10^10-100',2)  
print(res)

This will print 11. As the result of the entered expression is 11 in base-2.

**exp10(expression)**

Parses through a string expression and calculates it’s result in base-10.

expression – any arithmetical expression | should be **str** type

Returns – The resultant number in **int** or **str** type OR ‘Invalid number’ OR ‘Invalid base value’ OR ‘Invalid brackets’ OR ‘Undefined power operation’ OR ‘Cannot divide by zero’ OR ‘Operator missing operand’ OR ‘Invalid operators’ OR ‘Empty brackets’ OR ‘Brackets without any number’

Example:

from rithmetic import \*  
<br/>res = exp10('13.2((12.5-1.2\*4)\*3.12+7)-5.16/4\*2.1')  
print(res)

This will print 406.8078. As the result of the entered expression is 406.8078 in base-10.

**Disclaimer –** rithmetic functions do not round off any numbers and the max level of decimal points is set to 100. So, you will find some **str** type output values with a large number of decimal points (limited to a max of 100).

**exp** and **exp10** support both ‘^’ and ‘\*\*’ as exponent operators.
