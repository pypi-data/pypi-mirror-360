

def prac_1():
  print("""
  print("Prac 1: Write a program to implement logical gates AND, OR and NOT, with McCulloch-Pitts.")
  print("1.	For AND gate implementation:")
  x1 = [0, 0, 1, 1]
  x2 = [0, 1, 0, 1]
  w1 = [1, 1, 1, 1]
  w2 = [1, 1, 1, 1]
  threshold = 2

  print("x1 x2 w1 w2 Sum Output")
  for i in range(4):
      sum_input = x1[i] * w1[i] + x2[i] * w2[i]
      output = 1 if sum_input >= threshold else 0
      print(x1[i], x2[i], w1[i], w2[i], " ", sum_input, "  ", output)

# OR Gate using McCulloch-Pitts Neuron (with weights)
  print("2. OR Gate using McCulloch-Pitts Neuron (with weights)")
  

  x1 = [0, 0, 1, 1]      # Input 1
  x2 = [0, 1, 0, 1]      # Input 2
  w1 = [1, 1, 1, 1]      # Weight for x1
  w2 = [1, 1, 1, 1]      # Weight for x2
  t = 1                 # Threshold

  print("x1 x2 w1 w2  t  Output")

  for i in range(len(x1)):
      total = x1[i] * w1[i] + x2[i] * w2[i]
      output = 1 if total >= t else 0
      print(x1[i], x2[i], w1[i], w2[i], " ", t, "   ", output)


  # NOT Gate using McCulloch-Pitts Neuron (with weight)
  print("NOT Gate using McCulloch-Pitts Neuron (with weight)")
  x = [0, 1]       # Input
  w = [-1, -1]     # Weight (inverts the input)
  t = 0            # Threshold

  print("x  w  t  Output")

  for i in range(len(x)):
      total = x[i] * w[i]
      output = 1 if total >= t else 0
      print(x[i], w[i], t, " ", output)
  """)

def prac_2():
  print("""
  print("prac 2 :Write a program to implement Hebb’s learning rule.")
  !pip install numpy
  import numpy as np

  # Inputs
  x1 = np.array([1, 1, 1, -1, 1, -1, 1, 1, 1])   # First input
  x2 = np.array([1, 1, 1,  1, -1, 1, 1, 1, 1])   # Second input
  y = np.array([1, -1])                         # Target outputs

  # Initialize weights and bias
  weights = np.zeros(9, dtype=int)
  bias = 0

  # --- First input with target = 1 ---
  print("First input with target = 1")

  # Update weights using: w_new = w_old + x * y
  weights = weights + x1 * y[0]
  bias += y[0]

  print("Weights after 1st update:", weights)
  print("Bias after 1st update:   ", bias)
  print("\n")

  # --- Second input with target = -1 ---
  print("Second input with target = -1")

  # Update weights again using new input
  weights = weights + x2 * y[1]
  bias += y[1]

  print("Weights after 2nd update:", weights)
  print("Bias after 2nd update:   ", bias)
  """)




def prac_3():
  print("""
  import numpy as np
  import matplotlib.pyplot as plt

  class KohonenSOM:
      def __init__(self, x, y, input_len, learning_rate=0.5, radius=None, radius_decay=0.99, learning_rate_decay=0.99):
          # Initialize SOM grid and parameters
          self.x = x
          self.y = y
          self.input_len = input_len
          self.learning_rate = learning_rate
          self.radius = radius if radius is not None else max(x, y) / 2
          self.radius_decay = radius_decay
          self.learning_rate_decay = learning_rate_decay
          self.weights = np.random.rand(x, y, input_len)  # Random initial weights

      def train(self, data, num_iterations):
          for _ in range(num_iterations):
              sample = data[np.random.randint(len(data))]        # Pick a random input
              bmu_index = self.find_bmu(sample)                  # Find best matching unit
              self.update_weights(sample, bmu_index)             # Update BMU & neighbors
              self.learning_rate *= self.learning_rate_decay     # Decay learning rate
              self.radius *= self.radius_decay                   # Decay radius

      def find_bmu(self, sample):
          distances = np.linalg.norm(self.weights - sample, axis=-1)
          bmu_index = np.unravel_index(np.argmin(distances), (self.x, self.y))
          return bmu_index

      def update_weights(self, sample, bmu_index):
          for i in range(self.x):
              for j in range(self.y):
                  distance_to_bmu = np.linalg.norm(np.array([i, j]) - np.array(bmu_index))
                  if distance_to_bmu <= self.radius:
                      influence = np.exp(-distance_to_bmu**2 / (2 * (self.radius**2)))
                      self.weights[i, j] += influence * self.learning_rate * (sample - self.weights[i, j])

      def visualize(self):
          reshaped = self.weights.reshape(self.x * self.y, self.input_len)
          plt.imshow(reshaped, cmap='viridis')
          plt.colorbar()
          plt.title("SOM Weight Map")
          plt.show()

  # Example usage
  if __name__ == "__main__":
      data = np.random.rand(100, 3)  # 100 data points with 3 features (like RGB)
      som = KohonenSOM(x=10, y=10, input_len=3, learning_rate=0.5)
      som.train(data, num_iterations=1000)
      som.visualize()
      """)



def prac_4():
  print("""
  print("practical 4: Solve the Hamming Network, given the exemplar vectors.")
  import numpy as np

  # Predefined exemplar vectors (patterns)
  exemplar_vectors = np.array([
      [1, 0, 1, 0, 1, 1, 0, 1],
      [0, 1, 0, 1, 0, 0, 1, 0],
      [1, 1, 1, 1, 0, 1, 0, 0]
  ])

  # Input vector to compare
  input_vector = np.array([1, 0, 1, 1, 0, 1, 0, 1])

  # Function to calculate Hamming distance
  def hamming_distance(v1, v2):
      return np.sum(v1 != v2)

  # Function to find closest exemplar
  def hamming_network(input_vector, exemplar_vectors):
      distances = [hamming_distance(input_vector, ev) for ev in exemplar_vectors]
      min_index = np.argmin(distances)
      return min_index, distances[min_index]

  # Run the Hamming Network
  index, distance = hamming_network(input_vector, exemplar_vectors)

  # Output
  print(f"Closest match is exemplar at index {index} with Hamming distance {distance}.")
  """)



def prac_5():
  print("""
  print("prac 5:  Write a program for implementing BAM network.")
  import numpy as np

  # Define BAM class
  class BAM:
      def __init__(self):
          self.weights = None  # weight matrix between patterns A and B

      def train(self, patterns_A, patterns_B):
          # Initialize the weight matrix to zeros
          self.weights = np.zeros((patterns_A.shape[1], patterns_B.shape[1]))

          # Hebbian learning: outer product for each pair (A, B)
          for a, b in zip(patterns_A, patterns_B):
              self.weights += np.outer(a, b)

      def recall_A(self, pattern_B):
          # Recall pattern A from pattern B
          return np.sign(np.dot(pattern_B, self.weights.T))

      def recall_B(self, pattern_A):
          # Recall pattern B from pattern A
          return np.sign(np.dot(pattern_A, self.weights))

  # Example usage
  if __name__ == "__main__":
      # Training data: pattern pairs
      patterns_A = np.array([
          [1, 1, -1],
          [-1, 1, 1],
          [-1, -1, -1]
      ])

      patterns_B = np.array([
          [1, -1],
          [-1, 1],
          [1, 1]
      ])

      # Create BAM network and train it
      bam = BAM()
      bam.train(patterns_A, patterns_B)

      # Recall A from a given B
      test_pattern_B = np.array([1, -1])
      recalled_A = bam.recall_A(test_pattern_B)
      print("Recalled A from B", test_pattern_B, ":", recalled_A)

      # Recall B from a given A
      test_pattern_A = np.array([1, 1, -1])
      recalled_B = bam.recall_B(test_pattern_A)
      print("Recalled B from A", test_pattern_A, ":", recalled_B)
  """)




def prac_6():
    print("""
print("Prac six: Implement a program to find the winning neuron using MaxNet.")
import numpy as np

def maxnet(input_vector, epsilon=0.1, max_iterations=100):
    \"\"\"
    MaxNet algorithm to find the winning neuron.
    input_vector: Initial values (activations) of the neurons
    epsilon: Small positive inhibition factor (e.g., 0.1)
    Returns: Index of the strongest neuron (winner)
    \"\"\"
    activations = np.copy(input_vector)
    num_neurons = len(input_vector)

    for _ in range(max_iterations):
        # Inhibit each neuron by subtracting small value from all other neurons
        inhibition = epsilon * (np.sum(activations) - activations)
        new_activations = activations - inhibition

        # Remove negative values (simulate neuron being shut off)
        new_activations[new_activations < 0] = 0

        # If only one neuron is active (non-zero), we found the winner
        if np.count_nonzero(new_activations) == 1:
            break

        activations = new_activations

    return np.argmax(activations)  # Return index of winning neuron

# Example usage
input_vector = np.array([0.2, 0.5, 0.1, 0.7, 0.4])
winner_index = maxnet(input_vector)
print(f"The winning neuron is at index {winner_index} with activation {input_vector[winner_index]}")
""")




def prac_7():
  print("""
  print("practical 7:Implement De-Morgan’s Law" )
def de_morgans_law_1(A, B):
    # Law 1: ~(A OR B) == ~A AND ~B
    left = not (A or B)
    right = (not A) and (not B)
    return left, right

def de_morgans_law_2(A, B):
    # Law 2: ~(A AND B) == ~A OR ~B
    left = not (A and B)
    right = (not A) or (not B)
    return left, right

# Taking input from user
A_input = input("Enter A (True/False): ").strip().lower()
B_input = input("Enter B (True/False): ").strip().lower()

# Convert string to boolean
A = A_input == "true"
B = B_input == "true"

# Apply De Morgan's Law 1
result1 = de_morgans_law_1(A, B)
print("\nDe Morgan's Law 1: ~(A ∨ B) = ~A ∧ ~B")
print(f"~({A} ∨ {B}) = {result1[0]}")
print(f"~{A} ∧ ~{B} = {result1[1]}")
print(f"Law holds: {result1[0] == result1[1]}")

# Apply De Morgan's Law 2
result2 = de_morgans_law_2(A, B)
print("\nDe Morgan's Law 2: ~(A ∧ B) = ~A ∨ ~B")
print(f"~({A} ∧ {B}) = {result2[0]}")
print(f"~{A} ∨ ~{B} = {result2[1]}")
print(f"Law holds: {result2[0] == result2[1]}")
  """)




def prac_8():
  print("""
print("practical 8: Implement Union, Intersection, Complement, and Difference operations, on fuzzy sets)
# Fuzzy Union
def fuzzy_union(A, B):
    return {x: max(A.get(x, 0), B.get(x, 0)) for x in set(A).union(B)}

# Fuzzy Intersection
def fuzzy_intersection(A, B):
    return {x: min(A.get(x, 0), B.get(x, 0)) for x in set(A).intersection(B)}

# Fuzzy Complement
def fuzzy_complement(A):
    return {x: 1 - A[x] for x in A}

# Fuzzy Difference
def fuzzy_difference(A, B):
    return {x: min(A.get(x, 0), 1 - B.get(x, 0)) for x in set(A).union(B)}

# Example fuzzy sets
A = {'x1': 0.1, 'x2': 0.4, 'x3': 0.7}
B = {'x2': 0.5, 'x3': 0.2, 'x4': 0.8}

# Perform operations
union_result = fuzzy_union(A, B)
intersection_result = fuzzy_intersection(A, B)
complement_result_A = fuzzy_complement(A)
difference_result = fuzzy_difference(A, B)

# Display
print("Fuzzy Set A:", A)
print("Fuzzy Set B:", B)
print("\n--- Results ---")
print("Union (A ∪ B):", union_result)
print("Intersection (A ∩ B):", intersection_result)
print("Complement (A′):", complement_result_A)
print("Difference (A − B):", difference_result)
 """)





def prac_9():
    print("""
print("practical 9: Create Fuzzy relation by Cartesian product of any two fuzzy sets.")
# Define function to compute Cartesian product fuzzy relation
def cartesian_product_fuzzy_relation(A, B):
    \"\"\"
    Create fuzzy relation using Cartesian product.
    Each pair (x, y) gets min(A(x), B(y)) as membership.
    \"\"\"
    relation = {}
    for x in A:
        for y in B:
            relation[(x, y)] = min(A[x], B[y])
    return relation

# Example fuzzy sets
A = {'x1': 0.7, 'x2': 0.4, 'x3': 0.9}
B = {'y1': 0.6, 'y2': 0.8, 'y3': 0.5}

# Get the fuzzy relation
relation = cartesian_product_fuzzy_relation(A, B)

# Display results
print("Fuzzy Set A:", A)
print("Fuzzy Set B:", B)

print("\\nCartesian Product Fuzzy Relation (min(A(x), B(y))):")
for (x, y), value in relation.items():
    print(f"({x}, {y}): {value}")
""")

# Call the function




def prac_10():
    print("""
print("practical 10: Perform max-min composition on any two fuzzy relations.")
# Cartesian product: fuzzy relation from A to B
def cartesian_product_fuzzy_relation(A, B):
    return {(x, y): min(A[x], B[y]) for x in A for y in B}

# Max–Min Composition
def max_min_composition(R, S):
    T = {}
    x_elements = set(x for x, _ in R)
    y_elements = set(y for _, y in R)
    z_elements = set(z for _, z in S)

    for x in x_elements:
        for z in z_elements:
            min_values = []
            for y in y_elements:
                if (x, y) in R and (y, z) in S:
                    min_values.append(min(R[(x, y)], S[(y, z)]))
            if min_values:
                T[(x, z)] = max(min_values)
    return T

# Define fuzzy sets
A = {'x1': 0.7, 'x2': 0.4, 'x3': 0.9}
B = {'y1': 0.6, 'y2': 0.8, 'y3': 0.5}
C = {'z1': 0.5, 'z2': 0.9, 'z3': 0.3}

# Build relations
R = cartesian_product_fuzzy_relation(A, B)  # A × B
S = cartesian_product_fuzzy_relation(B, C)  # B × C

# Compose: A × C
T = max_min_composition(R, S)

# Output results
print("Fuzzy Set A:", A)
print("Fuzzy Set B:", B)
print("Fuzzy Set C:", C)

print("\nFuzzy Relation R (A × B):")
for key in sorted(R): print(f"{key}: {R[key]}")

print("\nFuzzy Relation S (B × C):")
for key in sorted(S): print(f"{key}: {S[key]}")

print("\nMax-Min Composition (R o S):")
for key in sorted(T): print(f"{key}: {T[key]}")
""")
    
