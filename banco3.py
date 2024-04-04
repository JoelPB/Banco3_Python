from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_cota(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo

        if valor > saldo:
            print("\n" + "\033[33m" + "@@@ Operação falhou! Você não tem saldo suficiente. @@@" + "\033[0;0m")

        elif valor > 0:
            self._saldo -= valor
            print("\n" + "\033[32m" + "=== Saque realizado com suceso! ===" + "\033[0;0m")
            return True
        else:
            print("\033[33m" + "\@@@ Operação falhou! O valor informado é inválido. @@@" + "\033[0;0m")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n" + "\033[32m" + "=== Depósito realizado com sucesso! ===" + "\033[0;0m")
        else:
            print("\n" + "\033[33m" + "@@@ Operação falhou! O valor informado é inválido. @@@" + "\033[0;0m")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        if valor > self.limite:
            print("\n" + "\033[33m" + "@@@ Operação falhou! O valor de saque excede o limite. @@@" + "\033[0;0m")
        elif numero_saques >= self.limite_saques:
            print("\n" + "\033[33m" + "@@@ Operação falhou! Número máximo de saques excedido. @@@" + "\033[0;0m")
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\n
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(cls, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = """\n
    ========== Menu ==========
    [d]\t\tDepositar
    [s]\t\tSacar
    [e]\t\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\t\tSair
    ==>\t
    """
    return input(menu)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n" + "\033[33m" + "@@@ Cliente não possui conta! @@@" + "\033[0;0m")
        return
    
    if len(cliente.contas) > 1:
        return escolher_conta_cliente(cliente.contas)

    return cliente.contas[0]


def escolher_conta_cliente(contas):
    conta_numero = int(input("Digite o número da conta do cliente: "))

    for conta in contas:
        if conta.numero == conta_numero:
            return conta

    print("\033[33m" + "@@@ Esta conta não pertence ao cliente! @@@" + "\033[0;0m")
    return


def depositar(clientes):
    cliente, conta = verificar_cliente_conta(clientes)

    if not cliente or not conta:
        return

    valor = float(input("Informe o valor depositado: "))
    transacao = Deposito(valor)

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cliente, conta = verificar_cliente_conta(clientes)

    if not cliente or not conta:
        return

    valor = float(input("Informe o valor saque: "))
    transacao = Saque(valor)

    cliente.realizar_transacao(conta, transacao)


def verificar_cliente_conta(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtar_cliente(cpf, clientes)

    if not cliente:
        print("\n" + "\033[33m" + "@@@ Cliente não encontrado! @@@" + "\033[0;0m")
        return None, None

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return cliente, None

    return cliente, conta


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtar_cliente(cpf, clientes)

    if not cliente:
        print("\n" + "\033[33m" + "@@@ Cliente não encontrado! @@@" + "\033[0;0m")
        return

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    print("\n=========== EXTRATO ===========")

    transacoes = conta.historico.transacoes
    extrato = ""

    if not transacoes:
        extrato = "\033[33m" + "Não foram realizadas movimentações." + "\033[0;0m"
    else:
        for transacao in transacoes:
            if transacao['tipo'] == str(Saque.__name__):
                extrato += "\033[31m" + f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}" + "\033[0;0m"
            else:
                extrato += "\033[32m" + f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}" + "\033[0;0m"

    print(extrato)
    print("\033[30;1;47m" + f"\nSaldo:\n\tR$ {conta.saldo:.2f}\n" + "\033[0;0m")
    print("===============================")


def criar_cliente(clientes):
    cpf = input("Iforme o CPF (somente números): ")
    usuario = filtar_cliente(cpf, clientes)

    if usuario:
        print("\033[33m" + "@@@Já existe um usuário com esse CPF! @@@" + "\033[0;0m")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Iforme o endereço (logradouro, nº - bairro - cidade/Sigla estado: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)
    print("\n" + "\033[32m" + "=== Cliente criado com sucesso! ===" + "\033[0;0m")


def filtar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtar_cliente(cpf, clientes)

    if not cliente:
        print("\n" + "\033[33m" + "@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@" + "\033[0;0m")
        return

    conta = ContaCorrente.nova_cota(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n" + "\033[32m" + "=== Conta criada com sucesso! ===" + "\033[0;0m")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(str(conta))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\033[33m" + "Opção inválida, por favor selecione novamente a operação desejada." + "\033[0;0m")


if __name__ == "__main__":
    main()