# Image perceptual tools

Based on perceptual hash, it bring some commands line tools.  

Compatibility with python >= 3.9 <= 3.14  

## Features  

- dupimg : find duplicate images based on perceptual hash in a directory.
- imgphash : print perceptual hash of a given image file name.
- qsimg : quick sort images in a directory based the perceptual distance between a reference image.
- simg : return the distance matrix between images of a directory based on the perceptual distance.


## Install

From PyPI
```
pip install img-phash-tools
```

From source  
```
pip install -r requirements.txt
pip install .
```

## dupimg

```
                                                                                                                                                                                            
 Usage: dupimg [OPTIONS] [DIRECTORY]                                                                                                                                                        
                                                                                                                                                                                            
 Find duplicates images with perceptual hash algorithms.                                                                                                                                    
                                                                                                                                                                                            
 It returns a list of filenames separated by a ';'                                                                                                                                          
 On the same line, the files are similar.                                                                                                                                                   
 On other lines, there is other duplicate files.                                                                                                                                            
                                                                                                                                                                                            
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   directory      [DIRECTORY]  The directory name. [default: .]                                                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --extensions                                                TEXT     List of extensions to filter separated by a coma. [default: jpg,jpeg,png,gif,webp,bmp]                              │
│ --mode                                                      TEXT     The hash mode : [averageHash, blockMeanHash, marrHildrethHash, pHash, radialVarianceHash]. [default: pHash]         │
│ --recurse                                   --no-recurse             Recurse over folders. [default: recurse]                                                                            │
│ --flip-v                                    --no-flip-v              Flip the image vertically (so hash will be flip resistant). [default: no-flip-v]                                    │
│ --flip-h                                    --no-flip-h              Flip the image horizontally (so hash will be flip resistant). [default: no-flip-h]                                  │
│ --block-mean-hash-mode                                      INTEGER  block_mean_hash_mode int, default:0 [default: 0]                                                                    │
│ --marr-hildreth-hash-alpha                                  FLOAT    marr_hildreth_hash_alpha float, default:2.0 [default: 2.0]                                                          │
│ --marr-hildreth-hash-scale                                  FLOAT    marr_hildreth_hash_scale float, default:1.0 [default: 1.0]                                                          │
│ --radial-variance-hash-sigma                                FLOAT    radial_variance_hash_sigma float, default:1.0 [default: 1.0]                                                        │
│ --radial-variance-hash-num-of-angle-line                    INTEGER  radial_variance_hash_num_of_angle_line int, default:180 [default: 180]                                              │
│ --install-completion                                                 Install completion for the current shell.                                                                           │
│ --show-completion                                                    Show completion for the current shell, to copy it or customize the installation.                                    │
│ --help                                                               Show this message and exit.                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## imgphash

```
                                                                                                                                                                                            
 Usage: imgphash [OPTIONS] [FILENAME]                                                                                                                                                       
                                                                                                                                                                                            
 Use to print the perceptual hash of an image.                                                                                                                                              
                                                                                                                                                                                            
 See https://www.phash.org or                                                                                                                                                               
 https://www.phash.org/docs/pubs/thesis_zauner.pdf                                                                                                                                          
 for more informations on the algorithms.                                                                                                                                                   
 It return the hashes into an integer, you can use hamming distance on his bits to find similar images.                                                                                     
 With --compare option, it will return the hamming distance between the two images.                                                                                                         
                                                                                                                                                                                            
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   filename      [FILENAME]  The file name. [default: .]                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --mode                                                      TEXT     The hash mode : [averageHash, blockMeanHash, marrHildrethHash, pHash, radialVarianceHash]. [default: pHash]         │
│ --flip-v                                    --no-flip-v              Flip the image vertically (so hash will be flip resistant). [default: no-flip-v]                                    │
│ --flip-h                                    --no-flip-h              Flip the image horizontally (so hash will be flip resistant). [default: no-flip-h]                                  │
│ --verbose                                   --no-verbose             Print more informations [default: no-verbose]                                                                       │
│ --compare                                                   TEXT     Compare to an other image filename and return distance.                                                             │
│ --block-mean-hash-mode                                      INTEGER  block_mean_hash_mode int, default:0 [default: 0]                                                                    │
│ --marr-hildreth-hash-alpha                                  FLOAT    marr_hildreth_hash_alpha float, default:2.0 [default: 2.0]                                                          │
│ --marr-hildreth-hash-scale                                  FLOAT    marr_hildreth_hash_scale float, default:1.0 [default: 1.0]                                                          │
│ --radial-variance-hash-sigma                                FLOAT    radial_variance_hash_sigma float, default:1.0 [default: 1.0]                                                        │
│ --radial-variance-hash-num-of-angle-line                    INTEGER  radial_variance_hash_num_of_angle_line int, default:180 [default: 180]                                              │
│ --install-completion                                                 Install completion for the current shell.                                                                           │
│ --show-completion                                                    Show completion for the current shell, to copy it or customize the installation.                                    │
│ --help                                                               Show this message and exit.                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## qsimg

```
                                                                                                                                                                                            
 Usage: qsimg [OPTIONS] [DIRECTORY] [REFERENCE]                                                                                                                                             
                                                                                                                                                                                            
 Quick Find Similar images with perceptual hash algorithms.                                                                                                                                 
                                                                                                                                                                                            
 It returns an ordered list by similarity with the reference image.                                                                                                                         
 In random mode, it will find a random reference.                                                                                                                                           
                                                                                                                                                                                            
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   directory      [DIRECTORY]  The directory name. [default: .]                                                                                                                           │
│   reference      [REFERENCE]  Reference file name. If given, it will sort only by similarity with this image.                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --rand                                      --no-rand                Use a random reference [default: rand]                                                                              │
│ --seed                                                      INTEGER  Seed for the random generator [default: -1]                                                                         │
│ --extensions                                                TEXT     List of extensions to filter separated by a coma. [default: jpg,jpeg,png,gif,webp,bmp]                              │
│ --mode                                                      TEXT     The hash mode : [averageHash, blockMeanHash, marrHildrethHash, pHash, radialVarianceHash]. [default: pHash]         │
│ --recurse                                   --no-recurse             Recurse over folders. [default: recurse]                                                                            │
│ --flip-v                                    --no-flip-v              Flip the image vertically (so hash will be flip resistant). [default: no-flip-v]                                    │
│ --flip-h                                    --no-flip-h              Flip the image horizontally (so hash will be flip resistant). [default: no-flip-h]                                  │
│ --block-mean-hash-mode                                      INTEGER  block_mean_hash_mode int, default:0 [default: 0]                                                                    │
│ --marr-hildreth-hash-alpha                                  FLOAT    marr_hildreth_hash_alpha float, default:2.0 [default: 2.0]                                                          │
│ --marr-hildreth-hash-scale                                  FLOAT    marr_hildreth_hash_scale float, default:1.0 [default: 1.0]                                                          │
│ --radial-variance-hash-sigma                                FLOAT    radial_variance_hash_sigma float, default:1.0 [default: 1.0]                                                        │
│ --radial-variance-hash-num-of-angle-line                    INTEGER  radial_variance_hash_num_of_angle_line int, default:180 [default: 180]                                              │
│ --verbose                                   --no-verbose             Print more values. [default: no-verbose]                                                                            │
│ --install-completion                                                 Install completion for the current shell.                                                                           │
│ --show-completion                                                    Show completion for the current shell, to copy it or customize the installation.                                    │
│ --help                                                               Show this message and exit.                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## simg

```
                                                                                                                                                                                            
 Usage: simg [OPTIONS] [DIRECTORY]                                                                                                                                                          
                                                                                                                                                                                            
 Find Similar images with perceptual hash algorithms.                                                                                                                                       
                                                                                                                                                                                            
 It returns a distance matrix between found images.                                                                                                                                         
                                                                                                                                                                                            
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   directory      [DIRECTORY]  The directory name. [default: .]                                                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --extensions                                                TEXT     List of extensions to filter separated by a coma. [default: jpg,jpeg,png,gif,webp,bmp]                              │
│ --mode                                                      TEXT     The hash mode : [averageHash, blockMeanHash, marrHildrethHash, pHash, radialVarianceHash]. [default: pHash]         │
│ --recurse                                   --no-recurse             Recurse over folders. [default: recurse]                                                                            │
│ --flip-v                                    --no-flip-v              Flip the image vertically (so hash will be flip resistant). [default: no-flip-v]                                    │
│ --flip-h                                    --no-flip-h              Flip the image horizontally (so hash will be flip resistant). [default: no-flip-h]                                  │
│ --block-mean-hash-mode                                      INTEGER  block_mean_hash_mode int, default:0 [default: 0]                                                                    │
│ --marr-hildreth-hash-alpha                                  FLOAT    marr_hildreth_hash_alpha float, default:2.0 [default: 2.0]                                                          │
│ --marr-hildreth-hash-scale                                  FLOAT    marr_hildreth_hash_scale float, default:1.0 [default: 1.0]                                                          │
│ --radial-variance-hash-sigma                                FLOAT    radial_variance_hash_sigma float, default:1.0 [default: 1.0]                                                        │
│ --radial-variance-hash-num-of-angle-line                    INTEGER  radial_variance_hash_num_of_angle_line int, default:180 [default: 180]                                              │
│ --install-completion                                                 Install completion for the current shell.                                                                           │
│ --show-completion                                                    Show completion for the current shell, to copy it or customize the installation.                                    │
│ --help                                                               Show this message and exit.                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Dev  
Install used dev tools with:  
```
pip install -r requirements.dev.txt
```

### Info  
colorMomentHash is not functional, it's a test.  

### Scripts  
All you need is into
```
./scripts/install.dev.sh
```
It will create main venv and venv for each python version we need to tests.  

You can now run lint and check scripts:
```
./scripts/lint.sh
./scripts/tests.sh
```
Before publishing you can test locally a CI:
```
./scripts/CI_all.sh
```
### Tests  
It use pytest, CLI commands are not fully tested.  

It seems to have different results for colorMomentHash and marrHildrethHash between Debian/Ubuntu (latest at 2025-07).  
It may be caused by an update in Ubuntu version (Ubuntu python version > Debian python version).  

You can run it with this command:
```
./scripts/tests.sh
```

### Coverage  
It does not find error raising tests but it's actually near 100%.  

You can run it with this command:
```
./scripts/tests_coverage.sh
```
