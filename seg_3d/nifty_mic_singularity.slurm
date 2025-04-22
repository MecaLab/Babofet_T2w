#!/bin/sh

# Generic configuration
#SBATCH --account='b219'
#SBATCH --partition=skylake
#SBATCH --time=4:00:00
#SBATCH -c 1
#SBATCH --mem-per-cpu=48G
#SBATCH -e %x_%j.err
#SBATCH -o %x_%j.out


COMMAND=$1
DATA=$2

singularity exec -B ${DATA}:/data /scratch/lbaptiste/softs/niftymic.multifact_latest.sif $COMMAND
  