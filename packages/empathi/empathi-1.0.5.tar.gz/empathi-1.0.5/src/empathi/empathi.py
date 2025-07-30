# Predict the function of the phage proteins in a given dataset.
if __package__ is None or __package__ == '':
    from embeddings import *
else:
    from .embeddings import *

import os
import time
import pickle
import joblib
import argparse
import itertools
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from multiprocessing.dummy import Pool as ThreadPool


# Parse arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Path to input file containing protein sequencs (.fa*) or protein embeddings (.pkl/.csv) that you wish to annotate (.pkl/.csv).')
    parser.add_argument('name', help='Predictions will be saved using this name in the results folder (no extension).')
    parser.add_argument('--only_embeddings', help='Whether to only calculate embeddings (no functional prediction).', action='store_true')
    parser.add_argument('-f', '--models_folder', help='Path to folder containing pretrained models. Default folder is ./models/', default="./models/")
    parser.add_argument('-o', '--output_folder', help='Path to the output folder. Default folder is ./empathi_out/', default="./empathi_out/")
    parser.add_argument('-m', '--mode', help='Which types of proteins you want to predict. Accepted arguments are "all" (default), "pvp", "rbp", "lysin", "regulator", ...', default="all")
    parser.add_argument('--custom', help='Instead of using --mode, you can specify the path to your own custom trained model (.pkl). The name you use will be used as the positive label.', default=False)
    parser.add_argument('-t', '--threads', type=int, help='Number of threads. Default 1.', default=1)
    parser.add_argument('-c', '--confidence', type=float_for_proba, help='Confidence threshold used for Annotation column. Default 0.50.', default=0.5)
    args = parser.parse_args()


    input_file = args.input_file
    models_folder = args.models_folder
    name = args.name
    only_embeddings = args.only_embeddings
    output_folder = args.output_folder
    mode = args.mode
    custom = args.custom
    threads = args.threads
    confidence = args.confidence

    return input_file, models_folder, name, only_embeddings, output_folder, mode, custom, threads, confidence

def float_for_proba(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x


# Load dataset we want to make predictions for
def load_dataset(input_file, threads):

    print("Loading dataset...")

    X_tests = []

    if threads == 1:
        if input_file.endswith(".pkl"):
            test = pd.read_pickle(input_file)

        if input_file.endswith(".csv"):
            test = pd.read_csv(input_file, index_col=0)
            test.columns = test.columns.astype(int)

        X_tests.append(test.loc[:, 0:1023])

    else:
        if input_file.endswith(".pkl"):
            test = pd.read_pickle(input_file)
            X_tests.append(test.loc[:, 0:1023])

        if input_file.endswith(".csv"):
            f = np.memmap(input_file)
            file_lines = sum(np.sum(f[i:i+(1024*1024)] == ord('\n')) for i in range(0, len(f), 1024*1024))
            chunk_size = (file_lines // threads) + 1

            for chunk in pd.read_csv(input_file, index_col=0, chunksize=chunk_size):
                chunk.columns = chunk.columns.astype(int)
                chunk = chunk.loc[:, 0:1023]
                X_tests.append(chunk)

    print("Done loading dataset.")

    return X_tests


def calc_embeddings(input_file, output_folder):

    lookup_p = Path(input_file)
    output_d = Path(output_folder)

    start=time.time()
    processor = sequence_processor(lookup_p, output_d)

    end=time.time()

    print("Total time: {:.3f}[s] ({:.3f}[s]/protein)".format(
        end-start, (end-start)/len(processor.lookup_ids)))

    return None



def _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=False, confidence=0.5):

    # If X_test is empty (ex. no predicted capsid proteins for major_capsid model), skip this model
    if X_test.shape[0] == 0:
        return all_preds

    # If model is hierarchical, set aside proteins that do not belong to parent annotation.
    # We wont waste resources making predictions for these proteins.
    if parent_anno:
        if not parent_anno in all_preds.columns: return all_preds

        keep = all_preds.index[all_preds.loc[:, parent_anno] > confidence]
        all_preds_ = all_preds.loc[~all_preds.index.isin(keep), :] # set aside non-anno proteins
        all_preds = all_preds.loc[all_preds.index.isin(keep), :]
        X_test = X_test.loc[X_test.index.isin(keep), :]

        if X_test.shape[0] == 0:
            return all_preds_

    # Load model and make predictions
    try:
        clf = joblib.load(os.path.join(models_folder, f"{anno}_svm.pkl"))
    except:
        print("Error loading models. Please make sure the empathi/models folder is in the correct location and well installed from HuggingFace. First, look at the size of the .pkl files in empathi/models folder. If they are all the same size, git-lfs did not install correctly. Reinstall git-lfs and reclone the HuggingFace repository. If the model files are properly installed, specifying the 'models_folder' argument explicitely might solve the problem.")

    preds = pd.DataFrame(clf.predict_proba(X_test), columns=clf.classes_, index=X_test.index).iloc[:,1]


    # Format annotations
    all_preds = _format_preds(preds, all_preds, mode, anno, confidence=confidence)

    # If hierarchical re-add proteins that did not belong to parent annotation
    if parent_anno:
        all_preds = pd.concat([all_preds, all_preds_]) # Re-add non-anno proteins
    return all_preds


# Make predictions for binary models and aggregate results
def _format_preds(preds, all_preds, mode, anno, confidence):
    preds = preds.loc[all_preds.index]
    all_preds.loc[:, anno] = preds

    if mode == anno: # assign "non-poi" (poi=protein of interest) as label if in binary mode (ex. pvp vs non-pvp).
        annotations = pd.Series(np.where(all_preds[anno] > confidence, anno, f"non-{anno}"), index=all_preds.index)
    else:
        annotations = pd.Series(np.where(all_preds[anno] > confidence, anno, ""), index=all_preds.index)

    if "Annotation" in all_preds.columns:
        all_preds.loc[:, "Annotation"] = all_preds.Annotation.str[:] + "|" + annotations.str[:]
        all_preds.loc[:, "Annotation"] = all_preds.Annotation.str.rstrip("|")
    else:
        all_preds.loc[:, "Annotation"] = annotations.str[:]

    return all_preds



# Predict all protein functions the user desires
def predict_functions(X_test, all_preds, models_folder, mode="all", confidence=0.5):

    print("Making predictions...")

    # phage virion proteins
    if (mode == "all") or (mode == "pvp"):
        anno_dict = {"pvp":False, "capsid":"pvp", "major_capsid":"capsid", "minor_capsid":"capsid","tail":"pvp",
                     "major_tail":"tail", "minor_tail":"tail", "baseplate":"tail", "tail_appendage":"tail",
                     "tail_sheath":"tail", "portal":"pvp", "head-tail_joining":"pvp"} #"collar":"pvp"

        for anno in anno_dict:
            print(f"Predicting {anno} proteins...")
            all_preds = _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=anno_dict[anno], confidence=confidence)


    # DNA-associated
    if (mode == "all") or (mode == "DNA-associated"):
        anno_dict = {"DNA-associated":False, "integration":"DNA-associated", "nuclease":"DNA-associated",
                     "DNA_polymerase":"DNA-associated", "terminase":"DNA-associated","annealing":"DNA-associated",
                    "helicase":"DNA-associated", "primase":"DNA-associated", "replication_initiation":"DNA-associated"}

        for anno in anno_dict:
            print(f"Predicting {anno} proteins...")
            all_preds = _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=anno_dict[anno], confidence=confidence)


    # Transcriptional regulators
    if (mode == "all") or (mode == "regulator"):
        anno_dict = {"transcriptional_regulator":False, "transcriptional_activator":"transcriptional_regulator",
                     "transcriptional_repressor":"transcriptional_regulator"}

        for anno in anno_dict:
            print(f"Predicting {anno} proteins...")
            all_preds = _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=anno_dict[anno], confidence=confidence)


    # Packaging and assembly proteins
    if (mode == "all") or (mode == "packaging"):
        print("Predicting packaging and assembly proteins...")
        all_preds = _predict(X_test, all_preds, models_folder, "packaging_assembly", mode, parent_anno=False, confidence=confidence)


    # adsorption-related proteins
    if (mode == "all") or (mode == "adsorption-related"):
        print("Predicting adsorption-related proteins...")
        all_preds = _predict(X_test, all_preds, models_folder, "adsorption-related", mode, parent_anno=False, confidence=confidence)


    # cell wall depolymerases
    if (mode == "all") or (mode == "cell_wall_depolymerase"):
        print("Predicting cell wall depolymerases...")
        all_preds = _predict(X_test, all_preds, models_folder, "cell_wall_depolymerase", mode, parent_anno=False, confidence=confidence)

    # RNA-associated
    if (mode == "all") or (mode == "RNA-associated"):
        print("Predicting RNA-associated proteins...")
        all_preds = _predict(X_test, all_preds, models_folder, "RNA-associated", mode, parent_anno=False, confidence=confidence)

    # nucleotide metabolism
    if (mode == "all") or (mode == "nucleotide_metabolism"):
        print("Predicting proteins associated to nucleotide metabolism...")
        all_preds = _predict(X_test, all_preds, models_folder, "nucleotide_metabolism", mode, parent_anno=False, confidence=confidence)

    # Internal and ejection proteins
    if (mode == "all") or (mode == "ejection"):
        print("Predicting internal and ejection proteins...")
        all_preds = _predict(X_test, all_preds, models_folder, "ejection", mode, parent_anno=False, confidence=confidence)


    # phosphorylation
    if (mode == "all") or (mode == "phosphorylation"):
        print("Predicting phosphorylation proteins...")
        all_preds = _predict(X_test, all_preds, models_folder, "phosphorylation", mode, parent_anno=False, confidence=confidence)


    # transferase
    if (mode == "all") or (mode == "transferase"):
        print("Predicting transferases...")
        all_preds = _predict(X_test, all_preds, models_folder, "transferase", mode, parent_anno=False, confidence=confidence)


    # reductase
    if (mode == "all") or (mode == "reductase"):
        print("Predicting reductases...")
        all_preds = _predict(X_test, all_preds, models_folder, "reductase", mode, parent_anno=False, confidence=confidence)


    # defense_systems
    if (mode == "all") or (mode == "defense_systems"):
        anno_dict = ["crispr", "anti-restriction", "sir2", "toxin", "super_infection"]

        for anno in anno_dict:
            print(f"Predicting {anno} proteins...")
            all_preds = _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=False, confidence=confidence)

    # lysis
    if (mode == "all") or (mode == "lysis"):
        anno_dict = {"lysis":False, "endolysin":"lysis", "lysis_inhibitor":"lysis", "holin":"lysis", "spanin":"lysis"}

        for anno in anno_dict:
            print(f"Predicting {anno} proteins...")
            all_preds = _predict(X_test, all_preds, models_folder, anno, mode, parent_anno=anno_dict[anno], confidence=confidence)

    #Create final annotation
    all_preds.loc[all_preds.Annotation == '', "Annotation"] = "unknown"
    all_preds.Annotation = all_preds.Annotation.str.lstrip("|")

    return all_preds


# Save predictions
def save_preds(preds, name, output_folder):

    print("Saving predictions to file...")

    preds[0].to_csv(os.path.join(output_folder, name, f"predictions_{name}.csv"))
    for pred in preds[1:]:
        pred.to_csv(os.path.join(output_folder, name, f"predictions_{name}.csv"), mode='a', header=False)

    print("Done saving predictions to file.")


def launch_per_thread(X_test, models_folder, mode, custom, confidence):

    #Remove entries with duplicate names
    if X_test.index.duplicated().sum() > 0:
        print(X_test.index.duplicated().sum(), "sequences with duplicate names were removed. Make sure this is normal as you may have lost some sequences. Here is the list of problematic IDs:", X_test[X_test.index.duplicated()].index)
    X_test = X_test.loc[~X_test.index.duplicated()]

    #Create empty dataframe to save predictions
    if mode == "all":
        all_preds = pd.DataFrame(index=X_test.index, columns=["Annotation", 'pvp','capsid', 'major_capsid', 'minor_capsid', 'tail', 'major_tail',
                   'minor_tail', 'baseplate', 'tail_appendage', 'tail_sheath', 'portal', 'head-tail_joining', 'DNA-associated', 'integration',
                   'nuclease', 'DNA_polymerase', 'terminase', 'annealing', 'helicase', 'primase', 'replication_initiation', 'transcriptional_regulator',
                   'transcriptional_activator', 'transcriptional_repressor', 'packaging_assembly', 'adsorption-related', 'cell_wall_depolymerase',
                   'RNA-associated', 'nucleotide_metabolism', 'ejection', 'phosphorylation', 'transferase', 'reductase', 'crispr', 'anti-restriction',
                   'sir2', 'toxin', 'super_infection', 'lysis', 'endolysin', 'lysis_inhibitor', 'holin', 'spanin'])
        all_preds.Annotation = ""
    else:
        all_preds = pd.DataFrame(index=X_test.index)

    if custom:
        with open(os.path.join(models_folder, custom), 'rb') as file:
            clf=pickle.load(file)
        preds = pd.DataFrame(clf.predict_proba(X_test), columns=clf.classes_, index=X_test.index).iloc[:, 1]
        preds = _format_preds(preds, all_preds, name, name)

    else:
        preds = predict_functions(X_test, all_preds, models_folder, mode, confidence)

    return preds

#Main function. Loads dataset and makes predictions.
def empathi(input_file, name, models_folder="models", only_embeddings=False, output_folder="empathi_out", mode="all", custom=False, threads=1, confidence=0.5):

    #Create output folder
    if not os.path.exists(os.path.join(output_folder, name)):
        os.makedirs(os.path.join(output_folder, name))

    #Load dataset
    if input_file.endswith((".fa", ".faa", ".fasta")): #input are protein sequences
        calc_embeddings(input_file, output_folder) #compute embeddings and save to file
        if only_embeddings:
            return None #stop before making predictions
        fname = f"{os.path.split(input_file)[1].rsplit('.', 1)[0]}.csv"
        X_tests = load_dataset(os.path.join(output_folder, fname), threads=threads)

    elif input_file.endswith((".pkl", ".csv")): #input are protein embeddings
        X_tests = load_dataset(input_file, threads=threads)

    else:
        print("Input file provided does not have an accepted extension (.pkl, .csv, .fa, .faa, .fasta).")

    pool = ThreadPool(threads)
    results = pool.starmap(launch_per_thread, zip(X_tests, itertools.repeat(models_folder, len(X_tests)), itertools.repeat(mode, len(X_tests)), itertools.repeat(custom, len(X_tests)), itertools.repeat(confidence, len(X_tests))))

    save_preds(results, name, output_folder)


def main():
    input_file, models_folder, name, only_embeddings, output_folder, mode, custom, threads, confidence = parse_args()
    empathi(input_file, name, models_folder, only_embeddings, output_folder, mode, custom, threads, confidence)

if __name__ == '__main__':
    #Load user args
    #input_file, models_folder, name, only_embeddings, output_folder, mode, custom, threads = parse_args()
    #empathi(input_file, name, models_folder, only_embeddings, output_folder, mode, custom, threads)
    main()
