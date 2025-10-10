#!/usr/bin/env python3
"""
Script principal pour parser les fichiers GeneWeb .gw
"""

import sys
import os

# Ajout du chemin courant pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import GeneWebParser

def main():
    """Main"""
    if len(sys.argv) != 2:
        print("Usage: python test.py <fichier.gw>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not os.path.exists(filename):
        print(f"Error : Folder doesn't exist {filename}")
        sys.exit(1)
    
    # Parsing du fichier
    parser = GeneWebParser()
    
    try:
        data = parser.parse_file(filename)
        
        #Show families
        if data.families:
            print(f"\nfamilies:")
            for i, family in enumerate(data.families[:3]):
                print(f"   {i+1}. {family}")
                if family.children:
                    print(f"      children: {len(family.children)}")
        
        # Exemple d'accès aux données
        if data.families:
            first_family = data.families[0]
            print(f"\n Details:")
            print(f"   Husband: {first_family.husband}")
            print(f"   Wife: {first_family.wife}")
            if first_family.wedding_date:
                print(f"   Marriage date: {first_family.wedding_date}")
            if first_family.wedding_place:
                print(f"   Place: {first_family.wedding_place}")
            
    except Exception as e:
        print(f"Parsing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("parsing the file.")
        sys.argv.append("test.gw")
    
    main()