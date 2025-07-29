from xcbench import MGCDB84.MGCDB84_Benchmark
import xcbench


calc = MGCDB84_Benchmark(basisset='def2-svp', xcfunctional=B3LYP,\
        dataset_path='xcbench/MGCDB84_Dataset' ,\
        dataset_types=['EA13','A24','BHPERI26','ISOMERIZATION20','IP13','AE18'])

rmsd,mad  = calc.compute_prediction()

f = open('rmsd_mad.dat','w')

for ii in range(len(rmsd)):
    f.write(str(calc.dataset_types[ii])+"   "+str(rmsd[ii])+"   "+str(mad[ii])+"\n")

f.close()























