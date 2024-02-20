import random
import hashlib


class Sampler:

    def __init__(self):
        #Initialise chaque echantillonneur avec une fonction de hachage aleatoire, pas de resultat encore, et pas termine
        self.hash_function = random.randint(0, 1000000)
        self.result = None
        self.done = False

    def __call__(self, identifier):
        # Calcule la valeur de hachage de l'identifiant en utilisant la fonction de hachage de l'echantillonneur
        hash_value = hash(str(identifier)) % self.hash_function
        if self.result is None or hash_value < self.hash_value:
            self.hash_value = hash_value
            self.result = identifier
        return self.result


def l2_sampler(stream, l2):
    # L2 sampler that takes a stream of identifiers and produces a sample list of size l2.

    l = len(set(stream))

    if(l>l2):

        # Initialize the list of samplers
        samplers = [Sampler() for _ in range(l2)]
        
        # Initialize the list of sampled identifiers
        sample_list = []

        # Loop over the stream of identifiers
        for i, identifier in enumerate(stream):
            # Remove the identifiers that have already been sampled
            stream_subset = stream[:i] + stream[i+1:] if i > 0 else stream[1:]
            stream_subset = [x for x in stream_subset if x not in sample_list]
        
            # Sample from the remaining identifiers
            for sampler in samplers:
                choice = random.choice(stream_subset)
                identifier = sampler(choice)
            
            # Add the smallest identifier to the sample list
            # smallest_id = min(sampler.result for sampler in samplers)

            results = [sampler.result for sampler in samplers]

            if results:
                smallest_id = min(results)

            while smallest_id in sample_list:

                if results:
                    results.remove(smallest_id)
                    if results:
                        smallest_id = min(results)
                    else:
                        new_list = [x for x in stream if x not in sample_list]
                        smallest_id = random.choice(new_list)
                else: 
                    new_list = [x for x in stream if x not in sample_list]
                    smallest_id = random.choice(new_list)

            sample_list.append(smallest_id)
            #stream_subset.remove(smallest_id)

            # Stop sampling when we reach the desired sample size
            if len(sample_list) == l2:
                break

        return sample_list
    
    else:
        
        new_l = l2 - len(set(stream))

        sample_list = []

        new_set = set(stream)

        for i in new_set:
            sample_list.append(i)

        # Initialize the list of samplers
        samplers = [Sampler() for _ in range(new_l)]
        

        # Loop over the stream of identifiers
        for i, identifier in enumerate(stream):
            # Remove the identifiers that have already been sampled
        
            # Sample from the remaining identifiers
            for sampler in samplers:
                choice = random.choice(stream)
                identifier = sampler(choice)
            
            # Add the smallest identifier to the sample list
            # smallest_id = min(sampler.result for sampler in samplers)

            results = [sampler.result for sampler in samplers]
            
            for j in results:
                sample_list.append(j)

            return(sample_list)

