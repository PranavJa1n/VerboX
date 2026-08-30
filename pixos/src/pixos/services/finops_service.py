from pixos.storage.system_repo import Budget

def check_department_budget(department : str):
    bud = Budget()
    data = bud.read(department_name=department)
    print(data)
    return data['current_spend'] < data['monthly_limit']

if __name__ == '__main__':
    print(check_department_budget("dept1"))