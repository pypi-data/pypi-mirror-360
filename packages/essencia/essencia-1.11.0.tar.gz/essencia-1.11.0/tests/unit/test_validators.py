"""
Unit tests for Brazilian validators.
"""
import pytest

from essencia.utils.validators import (
    validate_cpf,
    validate_cnpj,
    validate_email,
    validate_phone,
    validate_cep,
    format_cpf,
    format_cnpj,
    format_phone,
    format_cep,
)


class TestValidators:
    """Test Brazilian data validators."""
    
    @pytest.mark.unit
    def test_validate_cpf(self):
        """Test CPF validation."""
        # Valid CPFs
        assert validate_cpf("123.456.789-09") is True
        assert validate_cpf("12345678909") is True
        assert validate_cpf("111.222.333-96") is True
        
        # Invalid CPFs
        assert validate_cpf("123.456.789-00") is False
        assert validate_cpf("111.111.111-11") is False
        assert validate_cpf("000.000.000-00") is False
        assert validate_cpf("12345678901") is False
        assert validate_cpf("abc.def.ghi-jk") is False
        assert validate_cpf("") is False
        assert validate_cpf(None) is False
    
    @pytest.mark.unit
    def test_format_cpf(self):
        """Test CPF formatting."""
        assert format_cpf("12345678909") == "123.456.789-09"
        assert format_cpf("123.456.789-09") == "123.456.789-09"
        assert format_cpf("123456789-09") == "123.456.789-09"
        
        # Invalid CPFs
        with pytest.raises(ValueError):
            format_cpf("12345678901")
        with pytest.raises(ValueError):
            format_cpf("abc")
    
    @pytest.mark.unit
    def test_validate_cnpj(self):
        """Test CNPJ validation."""
        # Valid CNPJs
        assert validate_cnpj("11.222.333/0001-81") is True
        assert validate_cnpj("11222333000181") is True
        
        # Invalid CNPJs
        assert validate_cnpj("11.222.333/0001-80") is False
        assert validate_cnpj("11.111.111/1111-11") is False
        assert validate_cnpj("00.000.000/0000-00") is False
        assert validate_cnpj("") is False
        assert validate_cnpj(None) is False
    
    @pytest.mark.unit
    def test_format_cnpj(self):
        """Test CNPJ formatting."""
        assert format_cnpj("11222333000181") == "11.222.333/0001-81"
        assert format_cnpj("11.222.333/0001-81") == "11.222.333/0001-81"
        
        # Invalid CNPJs
        with pytest.raises(ValueError):
            format_cnpj("11222333000180")
        with pytest.raises(ValueError):
            format_cnpj("abc")
    
    @pytest.mark.unit
    def test_validate_phone(self):
        """Test phone validation."""
        # Valid phones
        assert validate_phone("(11) 98765-4321") is True
        assert validate_phone("(11) 8765-4321") is True
        assert validate_phone("11987654321") is True
        assert validate_phone("1187654321") is True
        assert validate_phone("+55 11 98765-4321") is True
        assert validate_phone("+5511987654321") is True
        
        # Invalid phones
        assert validate_phone("(11) 765-4321") is False
        assert validate_phone("987654321") is False
        assert validate_phone("abc") is False
        assert validate_phone("") is False
        assert validate_phone(None) is False
    
    @pytest.mark.unit
    def test_format_phone(self):
        """Test phone formatting."""
        assert format_phone("11987654321") == "(11) 98765-4321"
        assert format_phone("1187654321") == "(11) 8765-4321"
        assert format_phone("(11) 98765-4321") == "(11) 98765-4321"
        assert format_phone("+5511987654321") == "+55 (11) 98765-4321"
        
        # Invalid phones
        with pytest.raises(ValueError):
            format_phone("987654321")
        with pytest.raises(ValueError):
            format_phone("abc")
    
    @pytest.mark.unit
    def test_validate_cep(self):
        """Test CEP validation."""
        # Valid CEPs
        assert validate_cep("01234-567") is True
        assert validate_cep("01234567") is True
        assert validate_cep("12345-678") is True
        
        # Invalid CEPs
        assert validate_cep("1234-567") is False
        assert validate_cep("012345-67") is False
        assert validate_cep("abcde-fgh") is False
        assert validate_cep("") is False
        assert validate_cep(None) is False
    
    @pytest.mark.unit
    def test_format_cep(self):
        """Test CEP formatting."""
        assert format_cep("01234567") == "01234-567"
        assert format_cep("01234-567") == "01234-567"
        assert format_cep("12345678") == "12345-678"
        
        # Invalid CEPs
        with pytest.raises(ValueError):
            format_cep("1234567")
        with pytest.raises(ValueError):
            format_cep("abc")
    
    @pytest.mark.unit
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("user@example.com") is True
        assert validate_email("user.name@example.com") is True
        assert validate_email("user+tag@example.co.uk") is True
        assert validate_email("user_name@sub.example.com") is True
        
        # Invalid emails
        assert validate_email("user@") is False
        assert validate_email("@example.com") is False
        assert validate_email("user example@com") is False
        assert validate_email("user@.com") is False
        assert validate_email("") is False
        assert validate_email(None) is False