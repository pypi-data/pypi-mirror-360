import csv

import numpy as np


def parse_custom_csv_by_star(filepath):
    """
    Parse un fichier CSV avec une section de colonnes et organise les données 
    de manière à ce que la clé principale soit le star number.
    
    Args:
        filepath (str): Le chemin vers le fichier CSV.
    
    Returns:
        dict: Un dictionnaire avec le star number comme clé principale.
    """
    columns = []
    data = {}
    with open(filepath, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # Étape 1 : Extraire les colonnes
        inside_columns = False
        for line in lines:
            if line.startswith("#Columns"):
                inside_columns = True
            elif inside_columns and line.startswith("#("):  # Ligne avec un nom de colonne
                column_name = line.split(')',1)[-1].strip()
                columns.append(column_name)
            elif line.startswith("#"):  # Ignorer les autres commentaires
                continue
            else:
                break  # Fin de la section "Columns"

        # Étape 2 : Extraire les données
        for line in lines:
            if line.strip() and not line.startswith("#"):  # Ligne contenant des données
                values = line.split()
                star_number = values[0]  # La première valeur est le star number
                data[star_number] = {columns[i]: values[i] for i in range(1, len(values))}
    
    return data

def CMDFileRead(path):
    """
    Parse a CSV file and organise data so the main key is the star number
    
    Args:
        filepath (str): CSV file path.
    
    Returns:
        dict: dict with the star number as the main key.
    """

    filename = path.split(sep = '/')[-1]
    folder = path.split(sep = filename)
    title = ''
    with open(path, 'r', newline='') as inputFile:

        csv_reader = csv.reader(inputFile)
        # Fist step: divide the file
        _ = next(csv_reader)
        test = next(csv_reader)[0].split(sep = ' ')
        if (test[5] == 'STAR'):
            csv_reader = csv.reader(inputFile)
            i = 0
            count = 0
            lines = []
            for row in csv_reader:
                lines.append(row)
                if '##########################################' in row and count <= 1:
                    if count == 0:
                        # second step: write the title
                        vline = lines[2][0].split(sep = ' ')
                
                        val = [vline[2], vline[4], vline[5], vline[7]]
                        for j in range(len(val)):
                            val[j] = val[j].replace('.', '')
                            val[j] = val[j][0:4]
                        title = 'CMD_tGy' +str(val[0]) + 'SFR' + str(val[1]) + 'METp' + str(val[2]) + 'A_FE' + str(val[3])
                    i +=1
                    count +=1
                    lines = []

            if '-' in title:
                title = title.replace('-', '')
                title = title.replace('p','m')
            out_path =folder[0] + str(title) + '.csv'
        
            # third step: write data file
            with open (out_path, 'w', newline='') as writerFile:
                write_file = csv.writer(writerFile)
                
                write_file.writerows(lines)
        else : 
            out_path = path
    # last step: create the dict
    stardict = parse_custom_csv_by_star(out_path)
    return(stardict)

def parse_custom_csv_by_sp(filepath):
    """
    Parse un fichier CSV avec une section de colonnes et organise les données 
    de manière à ce que la clé principale soit le star number.
    
    Args:
        filepath (str): Le chemin vers le fichier CSV.
    
    Returns:
        dict: Un dictionnaire avec le star number comme clé principale.
    """
    columns = []
    data = {}
    with open(filepath, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # Étape 1 : Extraire les colonnes
        inside_columns = False
        for line in lines:
            # if line.startswith("#Columns"):
            #     inside_columns = True
            if line.startswith("#"):  # Ligne avec un nom de colonne
                column_name = line.split(' ')
                columns.append(column_name)
            # elif line.startswith("#"):  # Ignorer les autres commentaires
            #     continue
            else:
                break  # Fin de la section "Columns"
        col = []
        for i in range(len(columns[0])):
            if columns[0][i] != '' and columns[0][i] != '#':
                col.append(columns[0][i])
        col[-1] = col[-1].replace('\n', '')
        spnb = 1
        # Étape 2 : Extraire les données
        for line in lines:
            if line.strip() and not line.startswith("#"):  # Ligne contenant des données
                values = line.split()
                star_number = spnb 
                data[star_number] = {col[i]: values[i] for i in range(len(values))}
                spnb +=1
    
    return(data)

def RoundedValue(liste, nombre):
    return(min(liste, key=lambda x: abs(x - nombre)))

def gStar(StarDict):
    Tsol = 5.8*10**3
    gsol = 27.9 * 0.101972
    return(np.log10(float(StarDict['value of evolving mass in Mo'])) + 4 * np.log10(10**(float(StarDict['log(Teff)']))/Tsol) + np.log10(gsol) - float(StarDict['log(L/Lo)']))

def StarFinderWithCondition(dictionnary, conditions):
    """
    Find main keys of a dict containning required values

    Args:
        dictionnary (dict): Main dictionnary
        conditions (dict): Conditions dictionnary

    Returns:
        list: Dictionnary keys that contains conditions
    """
    return [
        mainkey for mainkey, sous_dico in dictionnary.items()
        if all(sous_dico.get(sous_cle) == valeur for sous_cle, valeur in conditions.items())
    ]



def FindSpiakidSp(stardict, nbstar, spfolder):
    files = []
    FileSpecDesc = 'SPIAKID_L_AMp'
    if spfolder[-1] != '/' : spfolder += '/' 
    M = stardict['1']['[Fe/H]']
    if '-' in M:
        M = M.replace('-','')
        FileSpecDesc = FileSpecDesc.replace('p', 'm')
    M = M.replace('.', '')[0:3]
    FileSpecGiants = spfolder + FileSpecDesc + M  + 'GIANTS.dat'
    FileSpecDwarfs = spfolder + FileSpecDesc + M  + 'DWARFS.dat'
 
 
    SpGiants = parse_custom_csv_by_sp(FileSpecGiants) 
    SpDwarfs = parse_custom_csv_by_sp(FileSpecDwarfs) 
    Tg, GLOGg = [], []
    Td, GLOGd = [], []
    for i in range(1, len(SpGiants)):
        Tg.append(int(SpGiants[i]['TEFF']))
        GLOGg.append(float(SpGiants[i]['GLOG']))

    Tg = sorted(set(Tg), key = lambda ele: Tg.count(ele))
    Tg.sort()

    GLOGg = sorted(set(GLOGg), key = lambda ele: GLOGg.count(ele))
    GLOGg.sort()
    
    for i in range(1, len(SpDwarfs)):
        Td.append(int(SpDwarfs[i]['TEFF']))
        GLOGd.append(float(SpDwarfs[i]['GLOG']))
        
    Td = sorted(set(Td), key = lambda ele: Td.count(ele))
    Td.sort()

    GLOGd = sorted(set(GLOGd), key = lambda ele: GLOGd.count(ele))
    GLOGd.sort()

    i = 1
    count = 0
    starsp = {}
    while count <= nbstar and i < len(stardict.keys()):
        Teff = 10**(float(stardict[str(i)]['log(Teff)']))
        
        glog = gStar(stardict[str(i)])
        starsp['star_'+str(count)] = {}
        starsp['star_'+str(count)]['Magiso'] = stardict[str(i)]['G']
        if RoundedValue([3,3.5], glog) == 3:
            Tsp = RoundedValue(Tg, Teff)
            gsp = RoundedValue(GLOGg, glog)
            
            cond = {}
            cond['TEFF'] = str(Tsp)
            cond['GLOG'] = str(gsp)+'0'
     
            inx = StarFinderWithCondition(SpGiants, cond)
            
            starsp['star_'+str(count)]['Spectrum'] = SpGiants[inx[0]]['FILENAME']
            starsp['star_'+str(count)]['Mag'] = float(SpGiants[inx[0]]['G'])
            starsp['star_'+str(count)]['ratio'] = 10**(-0.4*(float(stardict[str(i)]['G']) - float(SpGiants[inx[0]]['G'])))
            starsp['star_'+str(count)]['Temp'] = str(Tsp)
            files.append(inx[0])
        else:
          
            Tsp = RoundedValue(Td, Teff)
            gsp = RoundedValue(GLOGd, glog)
            
            cond = {}
            cond['TEFF'] = str(Tsp)
            cond['GLOG'] = str(gsp)+'0'
         
            inx = StarFinderWithCondition(SpDwarfs, cond)
           
            starsp['star_'+str(count)]['Spectrum'] = SpDwarfs[inx]['FILENAME']
            starsp['star_'+str(count)]['Mag'] = float(SpDwarfs[inx[0]]['G'])
            starsp['star_'+str(count)]['ratio'] = 10**(-0.4*(float(stardict[str(i)]['G']) - float(SpGiants[inx[0]]['G'])))
            starsp['star_'+str(count)]['Temp'] = str(Tsp)
            files.append(inx[0])
        count = len(files)
        i += 1
 
    return(files, starsp)