from pixos.storage.system_repo import Resource, Budget

ec2_hourly_rates = {
    # General Purpose - T2 Series
    "t2.nano": 0.0058,
    "t2.micro": 0.0116,
    "t2.small": 0.023,
    "t2.medium": 0.0464,
    "t2.large": 0.0928,
    
    # General Purpose - T3 Series
    "t3.nano": 0.0052,
    "t3.micro": 0.0104,
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "t3.xlarge": 0.1664,
    
    # General Purpose - T4g Series (AWS Graviton)
    "t4g.micro": 0.0084,
    "t4g.small": 0.0168,
    "t4g.medium": 0.0336,
    "t4g.large": 0.0672,
    
    # General Purpose - M Series
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
    "m6i.large": 0.096,
    "m6g.large": 0.077,
    "m7g.medium": 0.0404,
    
    # Compute Optimized - C Series
    "c5.large": 0.085,
    "c5.xlarge": 0.170,
    "c6i.large": 0.085,
    "c6g.large": 0.068,
    "c7g.medium": 0.0361,
    
    # Memory Optimized - R Series
    "r5.large": 0.126,
    "r5.xlarge": 0.252,
    "r6i.large": 0.126,
    "r6g.large": 0.1008,
    "r7g.medium": 0.0531
}

budget_details = {
    "dept1" : 5,
    "dept2" : 6
}

def main():
    res = Resource()
    print("Seeding Resource Table")
    for name, rate in ec2_hourly_rates.items():
        print(f"Writing : {name} - {rate}")
        res.create(instace_type=name, hourly_rate=rate)
    print("=" * 20)
    print("Resource Done!")
    bud = Budget()
    print("=" * 20)
    print("Seeding Budget Table")
    for department, limit in budget_details.items():
        print(f"Writing : {department} - {limit}") 
        bud.create(department_name=department, monthly_limit=limit, current_spend=0)
    print("=" * 20)
    print("Budget Done!")
    print("=" * 20)

if __name__ == '__main__':
    main()