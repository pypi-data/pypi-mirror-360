# -*- coding: utf-8 -*-

import argparse
import gzip
import sys

__version__ = "1.0.0"

def open_vcf(vcf_path):
    """Ouvre un fichier VCF compressé ou non."""
    return gzip.open(vcf_path, "rt") if vcf_path.endswith(".gz") else open(vcf_path, "r")

def summarize_vcf(vcf_file, chr_filter=None, range_filter=None):
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
                pos = int(parts[1])

                # Filtrage par chromosome
                if chr_filter and chrom not in chr_filter:
                    continue

                # Filtrage par intervalle
                if range_filter:
                    start, end = range_filter
                    if not (start <= pos <= end):
                        continue

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
        prog="etiennevar",
        description="🧬 etiennevar : Un outil simple pour résumer les fichiers VCF (compressés ou non).\n"
                    "Utilisez --summary pour obtenir un aperçu rapide du nombre de variants et des chromosomes présents.\n"
                    "Vous pouvez aussi filtrer par chromosome (--chr) ou par intervalle (--range).",
        epilog="Développé par Etienne Kabongo • Version 1.0.0"
    )
    parser.add_argument("vcf_file", help="Chemin vers le fichier VCF (.vcf ou .vcf.gz)")
    parser.add_argument("--summary", action="store_true", help="Afficher un résumé du fichier VCF")
    parser.add_argument("--version", action="store_true", help="Afficher la version de l'outil")
    parser.add_argument("--chr", nargs="+", help="Filtrer par un ou plusieurs chromosomes (ex: --chr 1 2 X)")
    parser.add_argument("--range", nargs=2, metavar=("START", "END"), type=int, help="Filtrer les variants par position (ex: --range 1000 5000)")

    args = parser.parse_args()

    if args.version:
        print(f"etiennevar version {__version__}")
        sys.exit()

    if args.summary:
        summarize_vcf(args.vcf_file, chr_filter=args.chr, range_filter=args.range)
    else:
        print("Utilisez l'option --summary pour afficher le résumé du VCF.")

if __name__ == "__main__":
    main()

