import sys
from backend.contradiction_detection.stage1 import Stage1
from backend.contradiction_detection.stage2 import Stage2
# 1. Define the test suite
# Each test case is a list of size 2: [Statement A, Statement B]
TEST_SUITE = {
    "unrelated": [
        [
            "The Hubble Space Telescope was launched into low Earth orbit in 1990.",
            "Baking a sourdough bread requires a long fermentation process."
        ],
        [
            "Python uses automatic garbage collection for memory management.",
            "The Great Barrier Reef is the world's largest coral reef system."
        ]
    ],
    "related_and_non_contradictory": [
        [
            "The company's quarterly revenue increased by 15% compared to last year.",
            "The company's quarterly sales increased by 15% compared to last year."
        ],
        [
            "Regular cardiovascular exercise strengthens the heart muscle over time.",
            "Running three times a week helps lower resting heart rates."
        ]
    ],
    "related_and_contradictory": [
        [
            "The retail store closed down all physical locations due to bankruptcy.",
            "All physical storefronts of the retailer are open and operating on normal hours."
        ],
        [
            "Clinical trial data showed that the new drug completely cured the infection.",
            "Clinical trial data showed that the new drug cannot cure the infection."
        ]
    ],
    "custom": [
        [
            "scale the deployments",
            "revoke the deployments"
        ],
        [
            "scale the deployments",
            "scale the deployments by size 2"
        ]
    ]
}

# Dummy pipeline function for illustration (Replace this with your actual function import)
def pipeline(statements: list[str]) -> None:
    statement_a = statements[0]
    statement_b = statements[1]

    node1 = Stage1()
    node2 = Stage2()

    if(node1.check(statements)):
        print("Related & : ")
        if(node2.check(statements)):
            print("Contradictory")
        else:
            print("Non - Contradictory")
    else:
        print('Unrelated - Not Execution stage 2')


# 2. Loop through the test suite and execute the pipeline
if __name__ == "__main__":
    print("🚀 Starting Contradiction Detection Test Suite...\n")
    
    # Iterate over each category (unrelated, related_and_non_contradictory, related_and_contradictory)
    for category, test_cases in TEST_SUITE.items():
        print(f"=== Category: {category.upper()} ===")
        
        for index, test_case in enumerate(test_cases, 1):
            print(f" Running Test Case #{index}")
            
            # Pass the list of size 2 directly into your pipeline function
            pipeline(test_case)
            
        print("-" * 50)
        
    print("\n✅ All test lists passed to the pipeline successfully.")
