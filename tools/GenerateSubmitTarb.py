#!/usr/bin/env python3

"""
Generate tarball for submission to arXiv.

Example:
$ ./GenerateSubmitTarb.py --tex letter.tex supplmat.tex --bbl letter.bbl

rgamba, 05/06/21
"""

import os, datetime, string, argparse, tarfile
from shutil import copyfile

def find_pattern(lines, pattern):
    return [line.strip('\n') for line in lines if pattern in line]

# taken from 
# https://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python
def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

parser = argparse.ArgumentParser()
parser.add_argument('--tex',    nargs='*', help='.tex files for the submission (required, at least one)', required=True)
parser.add_argument('--bbl',    help='bbl file (required)', required=True)
parser.add_argument('--outdir', help='path to output directory (optional)')
args = parser.parse_args()

# path of the submission dir -- if not user-input, use ddmmyyyy
dirpath = args.outdir
if dirpath == None:
    now = datetime.datetime.now() 
    dirpath = 'submission'+str(now.day)+str(now.month)+str(now.year)

# names of all tex
papernames= {args.tex[i] : args.tex[i].rsplit('/',1)[1] for i in range(len(args.tex))}
bblname   = args.bbl.rsplit('/',1)[1]


# path of first .tex
paperpath = args.tex[0].rsplit('/',1)[0]

print("Directory name:", dirpath)
print("Paper directory:",paperpath)
# create dir
try:
    os.mkdir(dirpath)
except FileExistsError:
    print("WARNING: Dir already exists, over-writing")

# fix .tex files input
# remove comments, change figure names

# patterns for figs, comments, bbl
incl_gr = "\includegraphics["
beg_fig = r"\begin{figure"
end_fig = r"\begin{figure"
comment = "%% "
biblio  = r"\bibliography"

abcs     = list(string.ascii_lowercase)

# copy the .bbl file to the new dir
print("* Copying .bbl file", args.bbl)
copyfile(args.bbl, dirpath+'/'+bblname)

# read in old file and find the patterns
for tx in args.tex:
    print("* Processing file", tx)
    with open(tx, 'r') as t:
        # all lines
        lns      = t.readlines()
        # find lines starting with %%
        lns_comm = find_pattern(lns, comment)
        # find figure lines
        lns_figs = find_pattern(lns, incl_gr)
        # find beginfigures
        lns_begf = find_pattern(lns, beg_fig)
        # find endfigures
        lns_endf = find_pattern(lns, end_fig)
        # find biblio
        lns_bibl = find_pattern(lns, biblio)

    # create the new .tex in dir
    texnew = dirpath+'/'+papernames[tx]

    figN     = 0
    subpltN  = 0

    with open(texnew, 'w') as tnew:
        for line in lns:

            # \begin{figure} found, increment fig Number
            if line.strip('\n') in lns_begf: 
                figN = figN+1

            # \end{figure} found, restart counting subplots
            if line.strip('\n') in lns_endf:
                subpltN = 0

            # subplot found
            if line.strip('\n') in lns_figs:
                
                # find path and extension of figure
                figpath    = line.strip('\n').split("{")[1].split("}")[0]
                cpfigpath  = paperpath+'/'+figpath
                figext     = figpath.split('.')[-1]
                
                # rename it (based on name of .tex, figN and subpltN)
                nm         = tx.split('.')[0]
                newfigpath = 'fig'+nm+str(figN)+abcs[subpltN]+'.'+figext
                subpltN    = subpltN+1
                print("\t", cpfigpath, "-->", dirpath+'/'+newfigpath)

                # copy figure to dir
                copyfile(cpfigpath, dirpath+'/'+newfigpath)
                
                # replace figpath with newfig in line
                line = line.replace(figpath, newfigpath)

            # bibliography
            if line.strip('\n') in lns_bibl:
                line = r'\input{%s}' %bblname

            # remove comments at the end
            if line.strip('\n') in lns_comm:
                line = line.split(comment)[0]

            # write the line
            tnew.write(line) 

# tar the dir
make_tarfile(dirpath+'.tar.gz', dirpath)