CHAVE = 9753123456

def mascarar_numero(numero: int) -> int:
    """
    Mascarar um número de forma reversível usando uma combinação de
    operações matemáticas.

    Args:
        numero (int): O número a ser mascarado.

    Returns:
        int: O número mascarado.
    """
    # Adiciona a chave, multiplica e, finalmente, aplica a operação XOR.
    # A ordem das operações é importante para a reversibilidade.
    mascarado = (numero + CHAVE) * 7  # Operação de soma e multiplicação
    mascarado = mascarado ^ CHAVE    # Operação XOR

    return mascarado

def desmascarar_numero(numero_mascarado: int) -> int:
    """
    Desmascarar um número que foi processado pela função 'mascarar_numero'.
    
    Args:
        numero_mascarado (int): O número mascarado.

    Returns:
        int: O número original.
    """
    # A ordem das operações deve ser invertida para reverter o mascaramento.
    # Primeiro, desfazemos a operação XOR.
    desmascarado = numero_mascarado ^ CHAVE

    # Em seguida, desfazemos a multiplicação e a soma.
    # Desfazer a multiplicação por 7 é dividir por 7.
    # Desfazer a soma por CHAVE é subtrair a CHAVE.
    desmascarado = desmascarado // 7 - CHAVE

    return desmascarado