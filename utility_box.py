import numpy, math, time

class UtilityBox (object):
    @staticmethod
    def euclidean_generator(dimension=300, print_time=False): #100 will be plenty in our case
        start = time.time()
        matrix = numpy.empty([dimension+1, dimension+1])
        x = 0
        for i in range (0, dimension+1):
            for j in range (x, dimension+1):
                euclidean = math.sqrt(i*i + j*j)
                matrix[i][j] = euclidean
                matrix[j][i] = euclidean
            x+=1
        if print_time:  print ("Total time: "+str(time.time()-start)+" seconds") #TODO search a better one-liner for this
        return matrix