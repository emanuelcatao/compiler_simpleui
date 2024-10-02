from graphviz import Digraph

class AFD:
    class State:
        def __init__(self, name, is_initial=False, is_final=False):
            self.name = name
            self.is_initial = is_initial
            self.is_final = is_final

    class Transicao:
        def __init__(self, origin, destine, symbol):
            self.origin = origin
            self.destine = destine
            self.symbol = symbol

    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.final_states = set()
        self.initial_state = None
        
        #atributos auxiliares
        #self.visitados = []

    def states_by_name(self, state_name):
        for inner_state in self.states:
            if inner_state.name == state_name:
                return inner_state
        return None

    def add_state(self, name, is_initial=False, is_final=False):
        state = self.State(name, is_initial, is_final)
        self.states.add(state)
        if is_initial:
            self.initial_state = state
        if is_final:
            self.final_states.add(state)
        return state

    def add_transition(self, origin, destine, symbol):
        transicao = self.Transicao(origin, destine, symbol)
        #print(origin.name, destine.name, symbol)
        if origin not in self.transitions:
            self.transitions[origin] = []
        else:
            for transition in self.transitions[origin]:
                if transition.destine == destine and symbol == transition.symbol:
                    #print("Transição já existente!")
                    return
        self.transitions[origin].append(transicao)
        self.alphabet.add(symbol)

    def transicao_estendida(self, current_state, word):
        def transicao(state, symbol):
            if state in self.transitions:
                for transicao in self.transitions[state]:
                    if transicao.symbol == symbol:
                        return transicao.destine
            return None
        if word == '':
            #auxiliar
            #self.visitados += [current_state]
            return current_state
        
        return transicao(self.transicao_estendida(current_state, word[:-1]), word[-1])

    def word_checker(self, word):
        return self.transicao_estendida(self.initial_state, word).is_final

    def plot(self, name):
        dot = Digraph(format='png')
        dot.attr(rankdir='LR', dpi='300', nodesep="1", ranksep="10", splines='true')

        states = self.states

        dot.node('seta', shape='point', width='0.3', style='invis')
        
        for state in states:
            name_state = state.name
            is_initial = state.is_initial
            is_final = state.is_final

            shape = 'circle'
            fillcolor = "lightblue"
            if is_initial:
                shape = 'circle'
            elif is_final:
                shape = 'doublecircle'
                fillcolor = 'lightgreen'

            dot.node(name_state, fillcolor=fillcolor, shape=shape, style="filled")

        dot.edge('seta', 'q0', arrowhead='normal', style='bold', color='gray')

        for origin, transitions in self.transitions.items():
            for transicao in transitions:
                origin_name = origin.name
                destine_name = transicao.destine.name

                symbol = transicao.symbol.replace('"', '\\"').replace('^', '\\^').replace("\\","\\\\")

                dot.edge(origin_name, destine_name, label=symbol)

        out_name = 'automato' + name

        dot.render(out_name, view=True, cleanup=True, directory='./out', format='png', engine='dot')

    
