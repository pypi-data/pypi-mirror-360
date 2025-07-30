import pandas as pd

# P_U = (0.8,0.2)
# P_D = (0.3,0.7)
# P_C = lambda v: (0.9, 0.1) if (v[0] == v[1]) else (0.1, 0.9)
#
# data = {
#     'U': [0, 0, 0, 0, 1, 1, 1, 1],
#     'D': [0, 0, 1, 1, 0, 0, 1, 1],
#     'C': [0, 1, 0, 1, 0, 1, 0, 1],
#     # 'P': [0.7 * 0.5 * 0.9, 0.7 * 0.5 * 0.1, 0.7 * 0.5 * 0.1, 0.7 * 0.5 * 0.9,
#     #              0.3 * 0.5 * 0.1, 0.3 * 0.5 * 0.9, 0.3 * 0.5 * 0.9, 0.3 * 0.5 * 0.1]
# }
#
# def build_P(df):
#     probabilities = []
#     for index, row in df.iterrows():
#         u_val = int(row['U'])
#         d_val = int(row['D'])
#         c_val = int(row['C'])
#
#         probabilities.append(P_U[u_val] * P_D[d_val] * P_C((u_val, d_val))[c_val])
#
#     df_output = df.copy()
#     df_output['P(U,D,C)'] = probabilities
#
#     return df_output
#
#
#
# df_original = pd.DataFrame(data)
# df_original = build_P(df_original)
# print(df_original)

def get_joint_table_by_enumerate(df_original):
    df_dc_joint = df_original.groupby(['D', 'C'])['P(U,D,C)'].sum().reset_index()

    df_dc_joint.rename(columns={'P(U,D,C)': 'P(D,C)'}, inplace=True)

    joint_prob_table_dc = df_dc_joint.pivot_table(
        index='D',
        columns='C',
        values='P(D,C)',
        fill_value=0
    )

    joint_prob_table_dc.index.name = None
    joint_prob_table_dc.columns.name = None

    joint_prob_table_dc.columns = [f'C={col}' for col in joint_prob_table_dc.columns]
    joint_prob_table_dc.index = [f'D={idx}' for idx in joint_prob_table_dc.index]
    return joint_prob_table_dc

def get_joint_table(P_U, P_D, P_C):
    p_c0_d0 = (P_U[0] * P_D(0)[0] * P_C(0, 0)[0]) + (P_U[1] * P_D(1)[0] * P_C(1, 0)[0])
    p_c1_d0 = (P_U[0] * P_D(0)[0] * P_C(0, 0)[1]) + (P_U[1] * P_D(1)[0] * P_C(1, 0)[1])

    p_c0_d1 = (P_U[0] * P_D(0)[1] * P_C(0, 1)[0]) + (P_U[1] * P_D(1)[1] * P_C(1, 1)[0])
    p_c1_d1 = (P_U[0] * P_D(0)[1] * P_C(0, 1)[1]) + (P_U[1] * P_D(1)[1] * P_C(1, 1)[1])
    joint_prob_table_direct = pd.DataFrame(
        [[p_c0_d0, p_c1_d0], [p_c0_d1, p_c1_d1]],
        index=[f'D=0', f'D=1'],
        columns=[f'C=0', f'C=1']
    )
    return joint_prob_table_direct

def get_do_table(P_U, P_C):
    index_labels = ['D=0', 'D=1']
    column_labels = ['P(C = 0 | do(D))', 'P(C = 1 | do(D))']

    do_df = pd.DataFrame(index=index_labels, columns=column_labels)

    p_c0_do_d0 = P_C(0, 0)[0] * P_U[0] + P_C(1, 0)[0] * P_U[1]
    p_c1_do_d0 = P_C(0, 0)[1] * P_U[0] + P_C(1, 0)[1] * P_U[1]
    p_c0_do_d1 = P_C(0, 1)[0] * P_U[0] + P_C(1, 1)[0] * P_U[1]
    p_c1_do_d1 = P_C(0, 1)[1] * P_U[0] + P_C(1, 1)[1] * P_U[1]

    do_df["P(C = 0 | do(D))"] = [p_c0_do_d0, p_c0_do_d1]
    do_df["P(C = 1 | do(D))"] = [p_c1_do_d0, p_c1_do_d1]
    return do_df

def get_nature_bound(joint_prob_table_dc):
    p_c0_d0 = joint_prob_table_dc.iloc[0, 0] # P(C=0, D=0)
    p_c1_d0 = joint_prob_table_dc.iloc[0, 1] # P(C=1, D=0)
    p_c0_d1 = joint_prob_table_dc.iloc[1, 0] # P(C=0, D=1)
    p_c1_d1 = joint_prob_table_dc.iloc[1, 1] # P(C=1, D=1)

    p_d0 = p_c0_d0 + p_c1_d0 # P(D=0)
    p_d1 = p_c0_d1 + p_c1_d1 # P(D=1)

    # Nature bounds

    a_c0_d0 = p_c0_d0
    b_c0_d0 = p_c0_d0 + (1 - p_d0)

    a_c1_d0 = p_c1_d0
    b_c1_d0 = p_c1_d0 + (1 - p_d0)

    a_c0_d1 = p_c0_d1
    b_c0_d1 = p_c0_d1 + (1 - p_d1)

    a_c1_d1 = p_c1_d1
    b_c1_d1 = p_c1_d1 + (1 - p_d1)

    bound_df = pd.DataFrame(
        {
            'a(C=0;D)': [a_c0_d0, a_c0_d1],
            'b(C=0;D)': [b_c0_d0, b_c0_d1],
            'a(C=1;D)': [a_c1_d0, a_c1_d1],
            'b(C=1;D)': [b_c1_d0, b_c1_d1],
        },
        index=['D=0', 'D=1']
    )
    return bound_df

def Tian_Pearl_Bounds(joint_prob_table_dc):
    p_c0_d0 = joint_prob_table_dc.iloc[0, 0] # P(C=0, D=0)
    p_c1_d0 = joint_prob_table_dc.iloc[0, 1] # P(C=1, D=0)
    p_c0_d1 = joint_prob_table_dc.iloc[1, 0] # P(C=0, D=1)
    p_c1_d1 = joint_prob_table_dc.iloc[1, 1] # P(C=1, D=1)

    p_c0 = p_c0_d0 + p_c0_d1
    p_c1 = p_c1_d0 + p_c1_d1

    a_c0_d0 = max(p_c0_d0, p_c0 - p_c0_d1)
    b_c0_d0 = min(1 - p_c1_d0, p_c0 + p_c1_d1)
    a_c1_d0 = max(p_c1_d0, p_c1 - p_c1_d1)
    b_c1_d0 = min(1 - p_c0_d0, p_c1 + p_c0_d1)

    a_c0_d1 = max(p_c0_d1, p_c0 - p_c0_d0)
    b_c0_d1 = min(1 - p_c1_d1, p_c0 + p_c1_d0)

    a_c1_d1 = max(p_c1_d1, p_c1 - p_c1_d0)
    b_c1_d1 = min(1 - p_c0_d1, p_c1 + p_c0_d0)


    bound_df = pd.DataFrame(
    {
        'a(C=0;D)': [a_c0_d0, a_c0_d1],
        'b(C=0;D)': [b_c0_d0, b_c0_d1],
        'a(C=1;D)': [a_c1_d0, a_c1_d1],
        'b(C=1;D)': [b_c1_d0, b_c1_d1],
        },
        index=['D=0', 'D=1']
    )
    return bound_df

# bound_df = get_nature_bound(joint_prob_table_dc)
# print("\n------------Manski Bound---------------")
# print(bound_df)

# Tian-Pearl Bounds
# p_c0 = p_c0_d0 + p_c0_d1
# p_c1 = p_c1_d0 + p_c1_d1
#
# a_c0_d0 = max(p_c0_d0, p_c0 - p_c0_d1)
# b_c0_d0 = min(1 - p_c1_d0, p_c0 + p_c1_d1)
# a_c1_d0 = max(p_c1_d0, p_c1 - p_c1_d1)
# b_c1_d0 = min(1 - p_c0_d0, p_c1 + p_c0_d1)
#
# a_c0_d1 = max(p_c0_d1, p_c0 - p_c0_d0)
# b_c0_d1 = min(1 - p_c1_d1, p_c0 + p_c1_d0)
#
# a_c1_d1 = max(p_c1_d1, p_c1 - p_c1_d0)
# b_c1_d1 = min(1 - p_c0_d1, p_c1 + p_c0_d0)
#
#
# bound_df = pd.DataFrame(
#     {
#         'a(C=0;D)': [a_c0_d0, a_c0_d1],
#         'b(C=0;D)': [b_c0_d0, b_c0_d1],
#         'a(C=1;D)': [a_c1_d0, a_c1_d1],
#         'b(C=1;D)': [b_c1_d0, b_c1_d1],
#     },
#     index=['D=0', 'D=1']
# )
#
# print("------------Bound---------------")
# print(bound_df)