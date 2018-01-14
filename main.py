import copy
import random
import operator
import time

random.seed(time.time())
predicates = {}
sentences = []
sentence_arg = []
predicate_pos = {}
predicate_neg = {}
queries = []
n = 0
q = 0
predicate_count = 1
argument_count = 0


def add_to_KB(index, data):
    global predicate_count
    data = data.strip()
    data = data.replace(" ", "")
    data = data.split('|')
    p_list = []
    p_arg = []
    arg_maping = {}
    global argument_count
    for d in data:
        negative = 1
        temp = d
        if d[0] == '~':
            negative = -1
            temp = d[1:]
        temp = temp.replace(")", "")
        predicate = temp.split('(')
        if predicate[0] not in predicates:
            predicates[predicate[0]] = predicate_count
            predicate_count += 1
        p_list.append(negative*predicates[predicate[0]])
        arguments = predicate[1].split(",")
        # print(arguments)
        i = 0
        for argument in arguments:
            if not is_constant(argument):
                if argument not in arg_maping:
                    arg_maping[argument] = 'x' + str(argument_count)
                    argument_count += 1
                arguments[i] = arg_maping[argument]
            i += 1
        # print(arg_maping)
        # if len(arguments) == 1:
        #     print(arguments)
        # else:
        #     print(arguments)
        # print()
        # print(arguments)
        # for argument in arguments:
        # if len(arguments) == 1:
        #     p_arg.append((arguments[0]))
        # else:
        p_arg.append(tuple(arguments))
        # l = len(arguments)
        # constants = 0
        # for argument in arguments:
        #     if argument[0].isupper():
        #         constants += 1
        # if l == constants:
        #     is_constant.append()
        predicate_no = predicates[predicate[0]]
        if negative == 1:
            if predicate_no not in predicate_pos:
                predicate_pos[predicate_no] = [index]
            else:
                predicate_pos[predicate_no].append(index)
        else:
            if predicate_no not in predicate_neg:
                predicate_neg[predicate_no] = [index]
            else:
                predicate_neg[predicate_no].append(index)
    # if len(p_list) == 1:
    #     sentences.append((p_list[0]))
    # else:
    # print("END")
    sentences.append(tuple(p_list))
    sentence_arg.append(p_arg)


def preprocess(query):
    negative = -1
    query = query.replace(" ", "")
    if query[0] == "~":
        query = query[1:]
        negative = 1
    query = query.replace(")", "").split('(')
    if query[0] not in predicates:
        return [[]], [[]]
    p_no = predicates[query[0]]
    p = []
    constants = []
    p.append(tuple([negative*p_no]))
    try:
        query[1] = query[1].split(',')
    except:
        query[1] = [query[1]]

    for constant in query[1]:
        constants.append(constant)

    return p, [[tuple(constants)]]


def is_constant(s):
    if s[0].isupper():
        return True
    return False


# TODO: ignore predicates from same sentence
# e.g.: P(a, b) | ~P(x,y) & P(Jim, Kim)
# should not resolve a with x
def unify(p1, c1, p2, c2):
    # TODO: for every predicate of p1, check for double with in p1
    # TODO: and then check in p2, if present, resolve.
    # TODO: place predicates with constants at top of list
    combined_c = {}
    i = 0
    # print(p1, c1, p2, c2)
    count1 = {}
    for p in p1:
        if p not in count1:
            count1[p] = 1
        else:
            count1[p] += 1

    count2 = {}
    for p in p2:
        if p not in count2:
            count2[p] = 1
        else:
            count2[p] += 1

    # print(count1, count2)
    f_count1 = []
    f_count2 = []
    for count in count1.keys():
        if -count in count1:
            f_count1.append(abs(count))

    for count in count2.keys():
        if -count in count2:
            f_count2.append(abs(count))

    f_count1 = list(set(f_count1))
    f_count2 = list(set(f_count2))
    # print(f_count1, f_count2)
    for predicate in p1:
        abs_p = abs(predicate)
        if abs_p not in combined_c:
            if predicate > 0:
                combined_c[abs_p] = [[c1[i]], []]
            else:
                combined_c[abs_p] = [[], [c1[i]]]
        else:
            if predicate > 0:
                combined_c[abs_p][0].append(c1[i])
            else:
                combined_c[abs_p][1].append(c1[i])
        i += 1

    i = 0
    for predicate in p2:
        abs_p = abs(predicate)
        if abs_p not in combined_c:
            if predicate > 0:
                combined_c[abs_p] = [[c2[i]], []]
            else:
                combined_c[abs_p] = [[], [c2[i]]]
        else:
            if predicate > 0:
                combined_c[abs_p][0].append(c2[i])
            else:
                combined_c[abs_p][1].append(c2[i])
        i += 1
    # more than one possibility?
    # A(x) | A(y) ~A(John)
    resolution = {}
    var_dependency = []
    var_dependency_contain = {}
    # print(combined_c)
    more = []
    # remaining = [[], []]
    for predicate in combined_c.keys():
        if combined_c[predicate][0] == [] or combined_c[predicate][1] == []:
            continue
        if len(combined_c[predicate][0]) == 1 and len(combined_c[predicate][1]) == 1:
            c_1 = combined_c[predicate][0][0]
            c_2 = combined_c[predicate][1][0]
            l = len(c_1)
            for i in range(0, l):
                const1 = is_constant(c_1[i])
                const2 = is_constant(c_2[i])
                # print(c_1[i], const1, c_2[i], const2)
                if const1 and const2:
                    if c_1[i] != c_2[i]:
                        # return false
                        return [False, 'found']
                elif const1:
                    if c_2[i] not in resolution:
                        resolution[c_2[i]] = c_1[i]
                    else:
                        if c_1[i] != resolution[c_2[i]]:
                            # return false
                            return [False, 'found']
                elif const2:
                    if c_1[i] not in resolution:
                        resolution[c_1[i]] = c_2[i]
                    else:
                        if c_2[i] != resolution[c_1[i]]:
                            # return false
                            return [False, 'found']
                else:
                    # print("WHoa-----------------------------")
                    c_1_in_var_dependency = True
                    c_2_in_var_dependency = True

                    if c_1[i] not in var_dependency_contain:
                        c_1_in_var_dependency = False
                    if c_2[i] not in var_dependency_contain:
                        c_2_in_var_dependency = False

                    if c_1_in_var_dependency and c_2_in_var_dependency:
                        c1_index = -1
                        c2_index = -1
                        m = len(var_dependency)
                        for j in range(0, m):
                            if c_1[i] in var_dependency[j]:
                                c1_index = j
                            if c_2[i] in var_dependency[j]:
                                c2_index = j
                        if c1_index != c2_index:
                            for c in var_dependency[c2_index]:
                                var_dependency[c1_index].append(c)
                            del var_dependency[c2_index]

                    elif c_1_in_var_dependency:
                        var_dependency_contain[c_2[i]] = 1
                        for v in var_dependency:
                            if c_1[i] in v:
                                v.append(c_2[i])
                                break

                    elif c_2_in_var_dependency:
                        var_dependency_contain[c_1[i]] = 1
                        for v in var_dependency:
                            if c_2[i] in v:
                                v.append(c_1[i])
                                break
                    else:
                        var_dependency_contain[c_1[i]] = 1
                        var_dependency_contain[c_2[i]] = 1
                        temp = list()
                        temp.append(c_1[i])
                        temp.append(c_2[i])
                        var_dependency.append(temp)
                    # if c_1[i] not in var_dependency:
                    #     var_dependency[c_1[i]] = [c_2[i]]
                    # else:
                    #     var_dependency[c_1[i]].append(c_2[i])
                    # if c_2[i] not in var_dependency:
                    #     var_dependency[c_2[i]] = [c_1[i]]
                    # else:
                    #     var_dependency[c_2[i]].append(c_1[i])
                    # var_dependency[c_1[i]] = var_dependency[c_2[i]] = list(set(var_dependency[c_1[i]]) | set(var_dependency[c_2[i]]))
            # print(combined_c[predicate][0], combined_c[predicate][1])
        else:
            more.append(predicate)
            # print("Whoa --- you are yet to handel this ---- ")
            # print(predicate, combined_c[predicate])

    var_dependencies = [var_dependency]
    resolutions = [resolution]
    var_dependency_contains = [var_dependency_contain]
    # print(var_dependencies, var_dependency)
    # print(more)
    if more:
        # combined_c[more[0]][1].append(('John', 'Josh'))
        # print(combined_c)
        dict1 = {}
        dict2 = {}
        i = 0
        for predicate in p1:
            if predicate not in dict1:
                dict1[predicate] = [c1[i]]
            else:
                dict1[predicate].append(c1[i])
            i += 1
        i = 0
        for predicate in p2:
            if predicate not in dict2:
                dict2[predicate] = [c2[i]]
            else:
                dict2[predicate].append(c2[i])
            i += 1
        # print("CHECK")
        # print(dict1, dict2)
        for m in more:
            curr_use = 0
            t_r = []
            t_v_d = []
            t_v_d_c = []
            contains_one = False
            for res in resolutions:
                for c_1 in combined_c[m][0]:
                    for c_2 in combined_c[m][1]:
                        fail = False
                        if (m in f_count1) or (m in f_count2):
                            # print("atte")
                            # print(combined_c[m])
                            # print(c_1, c_2)
                            if m in dict1:
                                if -m in dict2:
                                    if c_1 in dict1[m] and c_2 in dict2[-m]:
                                        fail = False
                                        # print("okay")
                                    else:
                                        # print("Not okay 1")
                                        fail = True
                                else:
                                    # print("Not okay 2")
                                    fail = True
                            elif m in dict2:
                                if -m in dict1:
                                    if c_1 in dict2[m] and c_2 in dict1[-m]:
                                        fail = False
                                        # print("okay")
                                    else:
                                        fail = True
                                        # print("Not okay 3")
                                else:
                                    fail = True
                                    # print("Not okay 4")
                                # fail = True
                            # if c_1 in dict1[m] and c_2 in dict2[-m]:
                            # if (c_1 in c1) and (c_2 in c1):
                            #     fail = True
                            #     print("Not okay")
                            # else:
                            #     fail = False
                            #     print("OK")
                            pass
                        # if m in f_count2:
                        #     print("att")
                        #     print(combined_c[m])
                        #     print(c_1, c_2)
                        #     if (c_1 in c2) and (c_2 in c2):
                        #         fail = True
                        #         print("Not okay")
                        #     else:
                        #         fail = False
                        #         print("OK")
                        #     pass
                        if fail:
                            continue
                        temp_r = copy.deepcopy(res)
                        temp_v_d = copy.deepcopy(var_dependencies[curr_use])
                        temp_v_d_c = copy.deepcopy(var_dependency_contains[curr_use])
                        l = len(c_1)
                        # fail = False
                        for i in range(0, l):
                            const1 = is_constant(c_1[i])
                            const2 = is_constant(c_2[i])
                            # print(c_1[i], const1, c_2[i], const2)
                            if const1 and const2:
                                if c_1[i] != c_2[i]:
                                    # return false
                                    # TODO: change this to terminate loop
                                    fail = True
                                    break
                                    # return [False, 'found']
                            elif const1:
                                if c_2[i] not in temp_r:
                                    temp_r[c_2[i]] = c_1[i]
                                else:
                                    if c_1[i] != temp_r[c_2[i]]:
                                        # return false
                                        # TODO: change this to terminate loop
                                        fail = True
                                        break
                                        # return [False, 'found']
                            elif const2:
                                if c_1[i] not in temp_r:
                                    temp_r[c_1[i]] = c_2[i]
                                else:
                                    if c_2[i] != temp_r[c_1[i]]:
                                        # return false
                                        # TODO: change this to terminate loop instead
                                        fail = True
                                        break
                                        # return [False, 'found']
                            else:
                                # print("WHoa-----------------------------")
                                c_1_in_var_dependency = True
                                c_2_in_var_dependency = True

                                if c_1[i] not in temp_v_d:
                                    c_1_in_var_dependency = False
                                if c_2[i] not in temp_v_d:
                                    c_2_in_var_dependency = False

                                if c_1_in_var_dependency and c_2_in_var_dependency:
                                    c1_index = -1
                                    c2_index = -1
                                    m = len(temp_v_d)
                                    for j in range(0, m):
                                        if c_1[i] in temp_v_d[j]:
                                            c1_index = j
                                        if c_2[i] in temp_v_d[j]:
                                            c2_index = j
                                    if c1_index != c2_index:
                                        for c in temp_v_d[c2_index]:
                                            temp_v_d[c1_index].append(c)
                                        del temp_v_d[c2_index]

                                elif c_1_in_var_dependency:
                                    temp_v_d_c[c_2[i]] = 1
                                    for v in temp_v_d:
                                        if c_1[i] in v:
                                            v.append(c_2[i])
                                            break

                                elif c_2_in_var_dependency:
                                    temp_v_d_c[c_1[i]] = 1
                                    for v in temp_v_d:
                                        if c_2[i] in v:
                                            v.append(c_1[i])
                                            break
                                else:
                                    temp_v_d_c[c_1[i]] = 1
                                    temp_v_d_c[c_2[i]] = 1
                                    temp = list()
                                    temp.append(c_1[i])
                                    temp.append(c_2[i])
                                    temp_v_d.append(temp)
                        if not fail:
                            if temp_r != {} or temp_v_d or temp_v_d_c:
                                t_r.append(temp_r)
                                t_v_d.append(temp_v_d)
                                t_v_d_c.append(temp_v_d_c)
                            contains_one = True
                curr_use += 1
            if t_r or t_v_d or t_v_d_c:
                resolutions = copy.deepcopy(t_r)
                var_dependencies = copy.deepcopy(t_v_d)
                var_dependency_contains = copy.deepcopy(t_v_d_c)
            else:
                # print(resolutions, var_dependencies, var_dependency_contains)
                if not contains_one:
                    # print("null")
                    resolutions = []
                    var_dependencies = []
                    var_dependency_contains = []
                break

        # print(more, combined_c[more[0]])
        # print(var_dependencies)
        # print(resolutions)
        # return [True, 'found']
    # res = []
    # res = {}
    if not var_dependencies:
        if not resolutions:
            if not var_dependency_contains:
                # print("checking")
                # for predicate in combined_c.keys():
                #     for c_1 in combined_c[predicate][0]:
                #         for c_2 in combined_c[predicate][1]
                # print("From here")
                # print(p1, c1, p2, c2)
                return [False, 'found']
    #     var_dependencies.append([])
    # if not resolutions:
    #     resolutions.append({})
    to_delete = {}
    # print("check this")
    # print(var_dependencies, var_dependency, resolutions)
    # if var_dependencies[0] or resolutions[0]:
    #     pass
    # else:
    #     return [False, 'found']
    if var_dependencies[0]:
        i = 0
        for var_d in var_dependencies:
            # temp = {}
            jump = False
            for v in var_d:
                resolved = False
                res_c = ""
                for c in v:
                    if c in resolutions[i]:
                        if resolved:
                            if res_c != resolutions[i][c]:
                                # return false
                                to_delete[i] = 1
                                jump = True
                                break
                                # return [False, 'found']
                        else:
                            resolved = True
                            res_c = resolutions[i][c]
                if jump:
                    break
                if not resolved:
                    res_c = v[0]
                for c in v:
                    resolutions[i][c] = res_c
                # if resolved:
                #     for c in v:
                #         resolutions[i][c] = res_c
                # else:
                #     r = v[0]
                #     for c in v:
                #         temp[c] = r
            # res.append(temp)
            i += 1

    # print(resolutions)
    m = len(resolutions)
    # print(len(resolutions), len(var_dependencies), len(var_dependency_contains))
    combined_cs = []
    for k in range(0, m):
        if k not in to_delete:
            combined_c_i = copy.deepcopy(combined_c)
            for consts in combined_c_i:
                if combined_c_i[consts][0]:
                    j = 0
                    for t in combined_c_i[consts][0]:
                        l = len(t)
                        temp = list(t)
                        for i in range(0, l):
                            c = temp[i]
                            if not is_constant(c):
                                if c in resolutions[k]:
                                    temp[i] = resolutions[k][c]
                                # elif c in res:
                                #     temp[i] = res[c]
                        t = tuple(temp)
                        combined_c_i[consts][0][j] = t
                        j += 1

                if combined_c_i[consts][1]:
                    j = 0
                    for t in combined_c_i[consts][1]:
                        l = len(t)
                        temp = list(t)
                        for i in range(0, l):
                            c = temp[i]
                            if not is_constant(c):
                                if c in resolutions[k]:
                                    temp[i] = resolutions[k][c]
                                # elif c in res:
                                #     temp[i] = res[c]
                        t = tuple(temp)
                        combined_c_i[consts][1][j] = t
                        j += 1
            combined_cs.append(combined_c_i)
        else:
            combined_cs.append([])

    # print(combined_cs)

    if not combined_cs[0]:
        return [False, 'found']

    res_ps = []
    res_cs = []
    te = []
    for k in range(0, m):
        if k not in to_delete:
            const_maping = {}
            global argument_count
            res_p = []
            res_c = []
            temp = []
            combined_c_i = combined_cs[k]
            for consts in combined_c_i:
                if combined_c_i[consts][0]:
                    for t in combined_c_i[consts][0]:
                        if t not in combined_c_i[consts][1]:
                            res_p.append(consts)
                            li = []
                            for c in t:
                                if not is_constant(c):
                                    if c not in const_maping:
                                        const_maping[c] = 'x' + str(argument_count)
                                        argument_count += 1
                                    li.append(const_maping[c])
                                else:
                                    li.append(c)
                            res_c.append(tuple(li))
                            temp.append(t)
                        else:
                            index = combined_c_i[consts][1].index(t)
                            del combined_c_i[consts][1][index]

                if combined_c_i[consts][1]:
                    for t in combined_c_i[consts][1]:
                        res_p.append(-consts)
                        li = []
                        for c in t:
                            if not is_constant(c):
                                if c not in const_maping:
                                    const_maping[c] = 'x' + str(argument_count)
                                    argument_count += 1
                                li.append(const_maping[c])
                            else:
                                li.append(c)
                        res_c.append(tuple(li))
                        temp.append(t)
            res_ps.append(res_p)
            res_cs.append(res_c)
            te.append(temp)
    # print(res_ps, te)
    # print(res_ps, res_cs)
    # print("here")
    # print(res_ps, res_cs)
    # i = 0
    # new_res_ps = []
    # new_res_cs = []
    # for res_p in res_ps:
    #     temp_dict = {}
    #     j = 0
    #     c = res_cs[i]
    #     for p in res_p:
    #         if p not in temp_dict:
    #             temp_dict[p] = [c[j]]
    #         else:
    #             temp_dict[p].append(c[j])
    #         j += 1
    #     i += 1
    #     # print("check this")
    #     # print(temp_dict)
    #     for t in temp_dict.keys():
    #         temp_dict[t] = list(set(temp_dict[t]))
    #     s = sorted(temp_dict.items())
    #     temp_p = []
    #     temp_c = []
    #     for elem in s:
    #         p = elem[0]
    #         for c in elem[1]:
    #             temp_p.append(p)
    #             temp_c.append(c)
    #     new_res_ps.append(temp_p)
    #     new_res_cs.append(temp_c)
    #     # print(temp_dict)
    # # print("check new")
    # # print(new_res_ps, new_res_cs)
    # res_ps = new_res_ps
    # res_cs = new_res_cs
    for res_p in res_ps:
        if not res_p:
            return [True, 'found']
    # print("----------------\n\n")
    return [res_ps, res_cs]


def sort_predicate(curr_p, curr_c):
    len_p = []
    i = 0
    for p in curr_p:
        len_p.append((len(p), i))
        i += 1
    len_p.sort(key=operator.itemgetter(0))
    new_p = []
    new_c = []
    for index in len_p:
        new_p.append(curr_p[index[1]])
        new_c.append(curr_c[index[1]])
    # print("sorting")
    # print(curr_p, curr_c)
    # print(new_p, new_c)
    return new_p, new_c


def solve(out_f, query):
    # for query in queries:
    #     print(query)
    curr_predicates, curr_constants = preprocess(query)
    # query_predicate = copy.deepcopy(curr_predicates)
    # query_constants = copy.deepcopy(curr_constants)
    # print(curr_predicates, curr_constants)
    new_predicates = []
    new_constants = []
    came_across = {}
    sentences.append(curr_predicates[0])
    sentence_arg.append(curr_constants[0])
    global added
    added = []
    start = time.time()
    if not curr_predicates[0]:
        out_f.write('FALSE\n')
        return
    # print(predicate_pos)
    # print(predicate_neg)
    if curr_predicates[0][0] > 0:
        added.append(True)
        if curr_predicates[0][0] in predicate_pos:
            predicate_pos[curr_predicates[0][0]].append(last)
            added.append(True)
        else:
            added.append(False)
            predicate_pos[curr_predicates[0][0]] = [last]
        added.append(curr_predicates[0][0])
    else:
        added.append(False)
        if -curr_predicates[0][0] in predicate_neg:
            added.append(True)
            predicate_neg[-curr_predicates[0][0]].append(last)
        else:
            added.append(False)
            predicate_neg[-curr_predicates[0][0]] = [last]
        added.append(-curr_predicates[0][0])
    # print(predicate_pos)
    # print(predicate_neg)
    # for q in curr_predicates:
    while curr_predicates:
        i = 0
        now = time.time()
        if (now-start) > 6.0:
            out_f.write('FALSE\n')
            return
        # last_use = 0
        for predicate in curr_predicates:
            # index = int(random.uniform(0, len(predicate)))
            # index = 0
            # print(index, predicate[index])
            # print(curr_constants[i])
            temp_c = []
            map_count = 0
            reverse_maping = {}
            for consts in curr_constants[i]:
                li = []
                for c in consts:
                    if not is_constant(c):
                        if c not in reverse_maping:
                            reverse_maping[c] = 'y' + str(map_count)
                            map_count += 1
                        li.append(reverse_maping[c])
                    else:
                        li.append(c)
                temp_c.append(tuple(li))
            # print(temp_c)

            if predicate not in came_across:
                came_across[predicate] = [temp_c]
            else:
                if temp_c in came_across[predicate]:
                    i += 1
                    continue
                else:
                    came_across[predicate].append(temp_c)
            l = len(predicate)
            # if last_use >= l:
                # last_use = 0
            # random.uniform(0, l)
            # last_use = random.randint(0, l - 1)
            rand = random.randint(0, 2)
            if rand:
                index = int(random.uniform(0, l))
                if index == l:
                    index = 0
            else:
                index = 0
            p_no = predicate[index]
            # else:
            #     p_no = predicate[0]
            # last_use = 0
            # done = {}
            # for index in range(0, l):
            #     p_no = predicate[index]
            #     if p_no in done:
            #         continue
            #     done[p_no] = 1
            if p_no < 0:
                if -p_no in predicate_pos:
                    for p in predicate_pos[-p_no]:
                        unified = unify(predicate, curr_constants[i], sentences[p], sentence_arg[p])
                        if unified[0] == True:
                            # print('TRUE1')
                            out_f.write('TRUE\n')
                            return
                        elif unified[0] == False:
                            # print('FALSE')
                            # i += 1
                            continue
                        # print(unified)
                        unified_0 = unified[0]
                        unified_1 = unified[1]
                        l = len(unified[0])
                        for k in range(0, l):
                            tup = tuple(unified_0[k])
                            # if tup == query_predicate and unified == unified_1[k]:
                            #     print('FALSE')
                            #     out_f.write('FALSE\n')
                            #     return
                            new_predicates.append(tup)
                            new_constants.append(unified_1[k])
            elif p_no > 0:
                if p_no in predicate_neg:
                    for p in predicate_neg[p_no]:
                        unified = unify(predicate, curr_constants[i], sentences[p], sentence_arg[p])
                        if unified[0] == True:
                            # print('TRUE2')
                            out_f.write('TRUE\n')
                            return
                        elif unified[0] == False:
                            # print('FALSE')
                            # i += 1
                            continue
                        # print(unified)
                        unified_0 = unified[0]
                        unified_1 = unified[1]
                        l = len(unified[0])
                        for k in range(0, l):
                            tup = tuple(unified_0[k])
                            # if tup == query_predicate and unified == unified_1[k]:
                            #     print('FALSE')
                            #     out_f.write('FALSE\n')
                            #     return
                            new_predicates.append(tup)
                            new_constants.append(unified_1[k])
            i += 1
            # last_use += 1
        # print(new_predicates, new_constants)
        # print()
        # time.sleep(5)
        # new_predicates, new_constants = sort_predicate(new_predicates, new_constants)
        curr_predicates = copy.deepcopy(new_predicates)
        curr_constants = copy.deepcopy(new_constants)
        new_predicates = []
        new_constants = []
        # print("-------------------------------------------------")
        # time.sleep(30)
    # print('FALSE')
    out_f.write('FALSE\n')
    return


def read_data():
    with open('input25.txt', 'r') as f:
        q = int(f.readline())
        for i in range(0, q):
            queries.append(f.readline().strip())

        n = int(f.readline())
        for i in range(0, n):
            add_to_KB(i, f.readline())


read_data()
added = []
# print("UPDATE REPEATATION HANDELING")
# print("READ TODO in unify function")
# print("REMOVE DUPLICATE")
for s in predicate_pos:
    predicate_pos[s] = list(set(predicate_pos[s]))
for s in predicate_neg:
    predicate_neg[s] = list(set(predicate_neg[s]))
# print(queries)
out = open('output.txt', 'w')
last = len(sentences)
for query in queries:
    solve(out, query)
    del sentences[last]
    del sentence_arg[last]
    if added:
        if added[0]:
            if added[1]:
                del predicate_pos[added[2]][-1]
            else:
                del predicate_pos[added[2]]
        else:
            if added[1]:
                del predicate_neg[added[2]][-1]
            else:
                del predicate_neg[added[2]]
# print(predicates)
# print(sentences)
# print(sentence_arg)
# print(predicate_pos)
# print(predicate_neg)
