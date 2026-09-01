from pixos.core.db_engine import get_connection

class ASG():
    def __init__(self):
        self.conn = get_connection()

    def create(self, asg_name : str, desired_capacity : int):
        with self.conn:
            self.conn.execute(
            """
            INSERT INTO autoscaling_groups
            Values (?, ?)
            """, (
                asg_name,
                desired_capacity
            )
            )

    def delete(self, asg_name : str):
        with self.conn:
            self.conn.execute("""
                    DELETE FROM autoscaling_groups
                    WHERE asg_name = ?
                    """, (asg_name,)
            )
    def update(self, asg_name : str , new_capacity : int):
        with self.conn:
            self.conn.execute(
                """
                UPDATE autoscaling_groups
                SET desired_capacity = ?
                WHERE asg_name = ?
                """, (new_capacity, asg_name)
            )

    def read(self, asg_name : str):
        with self.conn:
            capacity = self.conn.execute(
                """
                SELECT desired_capacity 
                FROM autoscaling_groups 
                WHERE asg_name = ?
                """, (asg_name,)
            ).fetchone()
        return dict(capacity)


class Instance():
    def __init__(self):
        self.conn = get_connection()

    def create(self, instance_id : str,asg_name : str):
        with self.conn:
            self.conn.execute("""
                    INSERT INTO ec2_instances
                    VALUES (?, ?)
                """, (
            instance_id,
            asg_name,
            ))
        
    def delete(self, instance_id):
        with self.conn:
            self.conn.execute("""
                    DELETE FROM ec2_instances
                    WHERE instance_id = ?
                """, (instance_id,)
                )
    def update(self, instance_id : str, asg_name : str):
        with self.conn:
            self.conn.execute(
                """
                UPDATE ec2_instances
                SET asg_name = ?
                WHERE instance_id = ?
                """, (asg_name, instance_id)
            )
    def read(self, instance_id : str):
        with self.conn:
            asg = self.conn.execute(
                    """
                    SELECT asg_name
                    FROM ec2_instances
                    WHERE instance_id = ?
                    """, (instance_id,)
                ).fetchone()
        return dict(asg)

class Resource():
    def __init__(self):
        self.conn = get_connection()

    def create(self, instace_type : str, hourly_rate : int):
        with self.conn:
            self.conn.execute("""
                INSERT INTO resource_costs
                VALUES (?, ?)
            """, (
                instace_type, hourly_rate
                )
            )
    def delete(self, instance_type : str):
        with self.conn:
            self.conn.execute("""
                DELETE FROM resource_costs
                WHERE instance_type = ?
            """, (instance_type,))

    def update(self, instance_type : str, hourly_rate : int):
        with self.conn:
            self.conn.execute(
                """
                 UPDATE resource_costs
                 SET hourly_rate = ?
                 WHERE instance_type = ?
                """, (hourly_rate, instance_type)
            )
    def read(self, instance_type : str):
        with self.conn:
            res = self.conn.execute(
                        """
                        SELECT hourly_rate
                        FROM resource_costs
                        WHERE instance_type = ?
                        """, (instance_type,)
                    ).fetchone()
        return dict(res)

class Budget():
    def __init__(self):
        self.conn = get_connection()

    def create(self, department_name : str, monthly_limit :int, current_spend :int):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO budgets
                VALUES (?, ?,  ?)
                """, (department_name, monthly_limit, current_spend)
            )
    def delete(self, department_name :str):
        with self.conn:
            self.conn.execute(
                """
                DELETE FROM budgets
                WHERE department_name = ?
                """, (department_name,)
            )
    def update(self, department_name : str, monthly_limit : int, current_spend : int):
        with self.conn:
            self.conn.execute(
                """
                UPDATE budgets
                SET monthly_limit = ?,
                current_spend = ?
                WHERE department_name = ?
                """, (monthly_limit, current_spend, department_name)
            )
    def read(self, department_name : str):
            with self.conn:
                bud = self.conn.execute(
                        """
                        SELECT monthly_limit, current_spend
                        FROM budgets
                        WHERE department_name = ?
                        """, (department_name,)
                    ).fetchone()
                bud = dict(bud)
                bud['department_name'] = department_name
            return bud


if __name__ == '__main__':
    asg = ASG()
    print(asg.read("asg1"))
    # asg.delete("asg2")
    # asg.create("asg1", 1)
    ins = Instance()
    print(ins.read("i2"))
    # ins.create("i2", "asg2")
    # ins.delete("i2")
    # asg.delete("asg2")
    res = Resource()
    print(res.read("type1"))
    # res.create("type1", 500)
    # res.update("type1", 200)
    # res.delete("type1")
    bud = Budget()
    print(bud.read("dept2"))
    # bud.create("dept2", 4000, 20000)
    # bud.update("dept2", 2000, 400)
    # bud.delete("dept2")
    # asg.update("asg2", 2)
    # ins.update("i2", "asg1")




