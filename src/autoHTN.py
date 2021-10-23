import pyhop
import json

def check_enough (state, ID, item, num):
    if getattr(state,item)[ID] >= num: return []
    return False

def produce_enough (state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

# name = name of recipe
# rule = contents of recipe
def make_method (name, rule):
    def method (state, ID):

        
        if 'Requires' in rule:
            for require in rule['Requires']:
                if not state[require]:
                    return False

        if 'Consumes' in rule:
            for consume in rule['Consumes']:
                if not state[consume] >= rule['Consumes'][consume]:
                    return False

        if 'Time' in rule:
            for timeAmount in rule['Time']:
                if not state[timeAmount] >= rule['Time'][timeAmount]:
                    return False
        return True
        # your code here
        

    return method

def declare_methods (data):
    # some recipes are faster than others for the same product even though they might require extra tools
    # sort the recipes so that faster recipes go first

    # your code here
    # hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)  
    recipes = data['Recipes']
    method_table = {}
    for r in recipes:
        name = r.replace(' ', '_')
        method = make_method(recipes[r], name)
        r_data = recipes[r]
        produce = list(r_data['Produces'])[0]
        
        if produce not in method_table:
            method_table[produce] = []
        m_tuple = (method, r_data['Time'])
        method_table[produce].append(m_tuple)
        method_table[produce].sort(key=lambda s : s[1])
    
    for i in method_table:
        name = 'produce_' + i
        for j in method_table[i]:
            pyhop.declare_methods(name, j[0])
    
def make_operator (rule): 
    requires = rule.get('Requires')
    if requires:
        s_requires = requires.keys()
        i_requires = requires.values()
    s_produces = rule['Produces'].keys()
    i_produces = rule['Produces'].values()
    time = rule['Time']

    def operator (state, ID):
        if state.time[ID] >= time:
            state.time[ID] -= time
            if requires:
                state[s_requires][ID] -= i_requires
            
            state[s_produces][ID] += i_produces
            return state
        return False
    return operator

def declare_operators (data):
    # your code here
    # hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
    recipes = data['Recipes']
    for r in recipes: 
        op = make_operator(recipes[r])
        pyhop.declare_operators(op)

def add_heuristic (data, ID):
    # prune search branch if heuristic() returns True
    # do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
    # e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
        # your code here
        return False # if True, prune this branch

    pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: time}

    for item in data['Items']:
        setattr(state, item, {ID: 0})

    for item in data['Tools']:
        setattr(state, item, {ID: 0})

    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})

    return state

def set_up_goals (data, ID):
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))

    return goals

if __name__ == '__main__':
    rules_filename = 'crafting.json'

    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, 'agent', time=239) # allot time here
    goals = set_up_goals(data, 'agent')

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    # pyhop.print_operators()
    # pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

