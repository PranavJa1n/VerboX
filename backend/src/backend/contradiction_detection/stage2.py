from backend.contradiction_detection.llm_util import AzureModel

class Stage2:
    def __init__(self):
        self.model = AzureModel()
        pass
    def check(self, statements):
        query = f"""
            statement_1 : {statements[0]}
            statement_2 : {statements[1]}
        """
        response = self.model.invoke(query)
        return response.is_contradictory


if __name__ == '__main__':
    obj = Stage2()
    print(obj.check(["scale the deployments", "imidiatly scale the deployments"]))