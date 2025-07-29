# brutils_py

**brutils_py** is a Python library for the generation, validation, and formatting of common Brazilian data used in documents, systems, and forms. It includes tools for working with CPF, CNPJ, RG, CNH, CEP, phone numbers, vehicle plates, and more.

It also offers integration with the [ViaCEP API](https://viacep.com.br) to verify the existence of a given CEP in real time.

---

## Features

- Generate and validate CPF (Cadastro de Pessoas Físicas)
- Generate and validate CNPJ (Cadastro Nacional da Pessoa Jurídica)
- Generate and validate RG (Registro Geral)
- Generate and validate CNH (Carteira Nacional de Habilitação)
- Generate, validate, and format CEP (Código de Endereçamento Postal)
- Check existence of CEP via ViaCEP API
- Generate and validate Título de Eleitor
- Generate and validate PIS and NIS numbers
- Generate and validate Brazilian phone numbers (mobile and landline)
- Generate and validate vehicle license plates (Mercosul and legacy formats)

---

## Installation

Install the library via pip:

```bash
pip install brutils_py
```

Note: This package requires Python 3.12 or higher.

## Development
To run tests locally, install the development dependencies:

```bash
pip install -e .[dev]
pytest
```

## License
This project is licensed under the MIT License. See LICENSE for more information.