#!/bin/bash
#SBATCH -J fetbet
#SBATCH -p batch
#SBATCH --ntasks-per-node=10
#SBATCH --mem-per-cpu=24G
#SBATCH -t 48:00:00
#SBATCH -N 1
#SBATCH -o ./fetbet_ens.out
#SBATCH -e ./fetbet_ens.err

# chargement des module
module purge
module load all

mkdir -p logs

eval "$(conda shell.bash hook)"
conda activate /envau/work/meca/users/cazzolla.m/conda_envs/eddy3

python run_baboons.py