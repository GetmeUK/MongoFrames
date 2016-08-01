from functools import reduce
import itertools


def p(i, sample_size, weights):
    """
    Given a weighted set and sample size return the probabilty that the
    weight `i` will be present in the sample.
    """

    # Determine the initial pick values
    weight_i = weights[i]
    weights_sum = sum(weights)

    # Build a list of weights that don't contain the weight `i`. This list will
    # be used to build the possible picks before weight `i`.
    other_weights = list(weights)
    del other_weights[i]

    # Calculate the probability
    probability_of_i = 0
    for picks in range(0, sample_size):

        # Build the list of possible permutations for this pick in the sample
        permutations = list(itertools.permutations(other_weights, picks))

        # Calculate the probability for this permutation
        permutation_probabilities = []
        for permutation in permutations:

            # Calculate the probability for each pick in the permutation
            pick_probabilities = []
            pick_weight_sum = weights_sum

            for pick in permutation:
                pick_probabilities.append(pick / pick_weight_sum)

                # Each time we pick we update the sum of the weight the next
                # pick is from.
                pick_weight_sum -= pick

            # Add the probability of picking i as the last pick
            pick_probabilities += [weight_i / pick_weight_sum]

            # Multiple all the probabilities for the permutation together
            permutation_probability = reduce(
                lambda x, y: x * y, pick_probabilities
                )
            permutation_probabilities.append(permutation_probability)

        # Add together all the probabilities for all permutations together
        probability_of_i += sum(permutation_probabilities)

    return probability_of_i


# Define a set of weights and a sample size
weights = [1, 2, 4, 8, 16, 32]
sample_size = 3

# Print out the probability of picking any of
for i, weight in enumerate(weights):
    probability_of_i = p(i, sample_size, weights)
    print(
        '{i} (w: {weight}, s: {sample_size}) ='.format(
            i=i,
            sample_size=sample_size,
            weight=weight
            ),
        probability_of_i
        )