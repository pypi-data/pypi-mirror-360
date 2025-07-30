---
slug: /use-cases/pii filter
sidebar_position: 3
---

# PII Filter

The PII (Personally Identifiable Information) filter is a utility designed to enhance privacy and security by masking personal information present in text. This filter marks sensitive data, such as names, addresses, or phone numbers, with **{'<strong>'}** opening and closing tags, effectively highlighting them.

Additionally, the filter offers customization by accepting an array of entities, allowing users to specify which specific types of personal information should be masked. By selectively applying masking to only the designated entities, the PII filter provides a flexible solution for safeguarding sensitive data within text-based content.

## Steps to integrate the pii filter

- Import Necessary Modules: Begin by importing the required modules for configuring the PII filter.

```python
from therix.core.pii_filter_config import PIIFilterConfig
```

- Instantiate the PII filter

Instantiate PII Filter: Create an instance of the PII Filter config class by specifying the desired entities to mask.

```python
pii_filter = PIIFilterConfig(config={entities : entities_to_mask})
```

Specify entities to mask (e.g., names and email address)

```python
entities_to_mask = [PERSON, EMAIL_ADDRESS]
```

- Add PII Filter to Agent: Use the .add() method to add the PIIFilter to your Therix agent.

```python
agent.add(pii_filter)
```

By following these steps and adjusting the parameters as needed, you can seamlessly integrate the PII filter into your Therix agent. Whether you need to mask specific types of personally identifiable information or ensure privacy and security in your text-based content, the PII filter offers a versatile solution for safeguarding sensitive data.

## List of valid entities

As of now therix supports masking of the following entities:

- **CREDIT_CARD**
  : A credit card number is between 12 to 19 digits.
- **CRYPTO**
  : A Crypto wallet number. Currently only Bitcoin address is supported.
- **DATE_TIME**
  : Absolute or relative dates or periods or times smaller than a day.
- **EMAIL_ADDRESS**
  : An email address identifies an email box to which email messages are delivered.
- **IBAN_CODE**
  : The International Bank Account Number (IBAN) is an internationally agreed system of identifying bank accounts across national borders to facilitate the communication and processing of cross-border transactions with a reduced risk of transcription errors.
- **IP_ADDRESS**
  : An Internet Protocol (IP) address (either IPv4 or IPv6).
- **NRP**
  : A person’s Nationality, religious or political group.
- **LOCATION**
  : Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains).
- **PERSON**
  : A full person name, which can include first names, middle names or initials, and last names.
- **PHONE_NUMBER**
  : A telephone number.
- **MEDICAL_LICENSE**
  : Common medical license numbers.
- **URL**
  : A Uniform Resource Locator, a pointer to a "resource" on the World Wide Web.

## Example

```python
pii_filter_agent = Agent(name="PII Filter Agent")

    (pii_filter_agent
        .add(YourConfigurations(config={  ''' Required configurations ''' }))
        .add(PIIFilterConfig(config={  ''' PII Filter added '''
            'entities': [ '''Add desired entities''' ]
    }))
    .save())
```

In this way we have sucessfully added PII Filter to our therix agent. Which masks the Personally Identifiable Information based on the entities provided.