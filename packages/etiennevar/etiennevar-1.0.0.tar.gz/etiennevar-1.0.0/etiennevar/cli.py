
# -*- coding: utf-8 -*-

import argparse
import gzip

def open_vcf(vcf_path):
    """Ouvre un fichier VCF compressé ou non."""
    if vcf_path.endswith(".gz"):
        return gzip.open(vcf_path, "rt")
    else:
        return open(vcf_path, "r")

def summarize_vcf(vcf_file):
    try:
        with open_vcf(vcf_file) as f:
            variant_count = 0
            chromosomes = set()

            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.strip().split("\t")
                if len(parts) < 5:
                    continue
                chrom = parts[0]
                chromosomes.add(chrom)
                variant_count += 1

        print("===== Résumé du fichier VCF =====")
        print(f"Nombre de variants : {variant_count}")
        print(f"Chromosomes présents : {', '.join(sorted(chromosomes))}")

    except FileNotFoundError:
        print(f"Erreur : le fichier '{vcf_file}' n'existe pas.")
    except Exception as e:
        print(f"Erreur lors du traitement du fichier : {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Outil de résumé pour les fichiers VCF (compressés ou non)."
    )
    parser.add_argument("vcf_file", help="Chemin vers le fichier VCF (.vcf ou .vcf.gz)")
    parser.add_argument("--summary", action="store_true", help="Afficher un résumé du fichier VCF")

    args = parser.parse_args()

    if args.summary:
        summarize_vcf(args.vcf_file)
    else:
        print("Utilisez l'option --summary pour afficher le résumé du VCF.")

