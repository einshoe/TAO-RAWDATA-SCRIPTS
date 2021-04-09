import numpy as np
import h5py
import argparse
import sys
import re

ordered = []
overrides = {}
label_map = {}
description_map = {}
units_map = {}
tao_bandpass_name = {}
delimiters = "<",">"
regexPattern = '|'.join(map(re.escape, delimiters))

def parse_keywords(line):
    keywords = {}
    rest = line
    pos1 = rest.find('=')
    while pos1 != -1:
        pos2 = rest.find('=',pos1+1)
        if pos2 == -1:
            pos3 = len(rest)
        else:
            pos3 = rest.rfind(' ',0,pos2)
        keyword = rest[:pos1]
        value = rest[pos1+1:pos3]
        keywords[keyword] = value
        rest = rest[pos3+1:]
        print("\t_k="+keyword+"=["+value+"]")
        pos1 = rest.find('=')
    return keywords

def scrape_metadata():
    with open("./scrapedata/overwrite_first_draft_dont_delete.txt", "r") as f:
        data = f.read()
        lines = re.split("\n", data)
        print("lines="+str(len(lines)))
        for index in range(len(lines)):
            line = lines[index].strip()
            if line == "":
                continue
            print("++"+line)
            keywords = parse_keywords(line)
            fieldname = keywords["fieldname"]
            overrides[fieldname] = keywords
    with open("./scrapedata/other_thirdhand_info.txt", "r") as f:
        data = f.read()
        lines = re.split("\n", data)
        for index in range(len(lines)):
            line = lines[index].strip()
            tokens = line.split(" ")

            if tokens[0].startswith("fieldname="):
                fieldname = tokens[0][len("fieldname="):]
                label = fieldname
                if tokens[1].startswith("label="):
                    label = tokens[1][len("label="):]
                if tokens[2].startswith("units="):
                    units = tokens[2][len("units="):]
                if tokens[3].startswith("description="):
                    description = tokens[3][len("description="):]
                    for index in range(4,len(tokens)):
                        description += " "+tokens[index]
                if not fieldname in description_map:
                    label_map[fieldname] = label
                    description_map[fieldname] = description
                    if units != "none":
                        units_map[fieldname] = units
                    print("fieldname from thirdhand=["+fieldname+"] description=["+description+"] label=["+label+"]")
                else:
                    print("SKIP fieldname from thirdhand=["+fieldname+"] description=["+description+"]")
                    pass

    with open("./scrapedata/output_files.html", "r") as f:
        data = f.read()
        lines = re.split(regexPattern, data)
        for index in range(len(lines)):
            line = lines[index]
            if line == 'span class="pre"':
                fieldname = lines[index+1]
                label = lines[index+5][2:]
                description = label
                units = ""
                pos1 = label.find("[")
                pos2 = label.find("]")
                if pos1 != -1:
                    units = label[pos1+1:pos2]
                    description = label[:pos1].strip()
                    if pos2 != len(label)-1:
                        description = label[:pos1].strip()+label[pos2+1:]
                    else:
                        description = label[:pos1].strip()
                print("metafield["+fieldname+"]"+description+" units="+units)
                description_map[fieldname] = description
                units_map[fieldname] = units

    with open("./scrapedata/module_user_routines_shark.f08", "r") as f:
        data = f.read()
        lines = re.split("\n", data)
        for index in range(len(lines)):
            line = lines[index].strip()
            if "::" in line and "!" in line:
                if line.startswith("real*4 ") or line.startswith("integer*4 ") or line.startswith("integer*8 "):
                    pos1 = line.find("::")
                    pos2 = line.find("!")
                    fieldname = line[pos1+2:pos2].strip()
                    label = line[pos2+1:].strip()
                    pos1 = label.find("[")
                    pos2 = label.find("]")
                    if pos1 != -1:
                        units = label[pos1+1:pos2]
                        description = label[pos2+1:].strip()
                    else:
                        units = ""
                        description = label
                    if not fieldname in description_map:
                        description_map[fieldname] = description
                        units_map[fieldname] = units
                        print("fieldname from f08=["+fieldname+"] description=["+description+"] units=["+units+"]")
                    else:
                        print("SKIP fieldname from f08=["+fieldname+"] description=["+description+"] units=["+units+"]")
                        pass

    with open("./scrapedata/module_user_routines_shark.f08", "r") as f:
        data = f.read()
        lines = re.split("\n", data)
        for index in range(len(lines)):
            line = lines[index].strip()
            if line.startswith("call hdf5_write_data(name//"):
                if line.endswith("&"):
                    line = line[0:-1]+lines[index+1].strip()[1:]
                line = line[28:]
                pos1 = line.find("'")
                fieldname = line[:pos1]
                label = line[pos1+1:]
                pos1 = label.find("'")
                label = label[pos1+1:]
                pos2 = label.find("'")
                pos1 = label.find("[")
                pos2 = label.find("]")
                if pos1 != -1:
                    units = label[pos1+1:pos2]
                    description = label[pos2+1:-2].strip()
                else:
                    units = ""
                    description = label
                if not fieldname in description_map:
                    description_map[fieldname] = description
                    units_map[fieldname] = units
                    print("LAST CHANCE fieldname from f08=["+fieldname+"] description=["+description+"] units=["+units+"]")
                else:
                    print("SKIP fieldname from f08=["+fieldname+"] description=["+description+"] units=["+units+"]")
                    pass

                print("LINE["+line+"] fieldname["+fieldname+"] description["+description+"]")
                

def get_scraped_label(name):
    if name in overrides:
        if "label" in overrides[name]:
            return overrides[name]["label"]
    if name.startswith("dust_"):
        return name[5:]+" (With Dust)"
    if name.startswith("nodust_"):
        return name[7:]
    if name in label_map:
        print("label_map["+name+"]="+label_map[name])
        return label_map[name]
    return name

def get_scraped_description(name):
    if name in description_map:
        return description_map[name]
    if name.startswith("dust_"):
        return name[5:]+" (With Dust)"
    if name.startswith("nodust_"):
        return name[7:]
    return name

def get_scraped_units(name):
    if name in units_map:
        return units_map[name]
    return ""

def get_scraped_group(group):
    # for array fieldnames belonging to groups
    if group in tao_bandpass_name:
        return tao_bandpass_name[group]
    return group

def get_scraped_groupname(name, default):
    if name in overrides:
        if "group" in overrides[name]:
            return overrides[name]["group"]
    return default

def get_scraped_order(name):
    for i in range(len(ordered)):
        if ordered[i] == name:
            return i+1

def print_attrs(name, obj):
    maxrows = 10
    firstcolumn=-1
    lastcolumn=-1
    print("####NAME["+name+"]="+str(obj.attrs.keys()))
    if name == 'galaxies' or name == 'Data' or str(name).endswith('Galaxies'):
       groups = {}
       groups["Band4_ALMA"] = 1
       groups["Band5_ALMA"] = 1
       groups["Band6_ALMA"] = 1
       groups["Band7_ALMA"] = 1
       groups["Band8_ALMA"] = 1
       groups["Band9_ALMA"] = 1
       groups["S450_JCMT"] = 1
       groups["S850_JCMT"] = 1
       groups["S250_Herschel"] = 1
       groups["S350_Herschel"] = 1
       groups["S450_Herschel"] = 1
       groups["S500_Herschel"] = 1
       groups["FUV_GALEX"] = 1
       groups["NUV_GALEX"] = 1
       groups["u_SDSS"] = 1
       groups["g_SDSS"] = 1
       groups["r_SDSS"] = 1
       groups["i_SDSS"] = 1
       groups["z_SDSS"] = 1
       groups["Y_VISTA"] = 1
       groups["J_VISTA"] = 1
       groups["H_VISTA"] = 1
       groups["K_VISTA"] = 1
       groups["W1_WISE"] = 1
       groups["W2_WISE"] = 1
       groups["W3_WISE"] = 1
       groups["W4_WISE"] = 1
       groups["I1_Spitzer"] = 1
       groups["I2_Spitzer"] = 1
       groups["I3_Spitzer"] = 1
       groups["I4_Spitzer"] = 1
       groups["P70_Herschel"] = 1
       groups["P100_Herschel"] = 1
       groups["P160_Herschel"] = 1

       tao_bandpass_name["Band4_ALMA"] = "ALMA Band4"
       tao_bandpass_name["Band5_ALMA"] = "ALMA Band5"
       tao_bandpass_name["Band6_ALMA"] = "ALMA Band6"
       tao_bandpass_name["Band7_ALMA"] = "ALMA Band7"
       tao_bandpass_name["Band8_ALMA"] = "ALMA Band8"
       tao_bandpass_name["Band9_ALMA"] = "ALMA Band9"
       tao_bandpass_name["S450_JCMT"] = "JCMT S450"
       tao_bandpass_name["S850_JCMT"] = "JCMT S850"
       tao_bandpass_name["S250_Herschel"] = "Herschel/SPIRE 250"
       tao_bandpass_name["S350_Herschel"] = "Herschel/SPIRE 350"
       tao_bandpass_name["S450_Herschel"] = "Herschel/SPIRE 450"
       tao_bandpass_name["S500_Herschel"] = "Herschel/SPIRE 500"
       tao_bandpass_name["FUV_GALEX"] = "GALEX FUV"
       tao_bandpass_name["NUV_GALEX"] = "GALEX NUV"
       tao_bandpass_name["u_SDSS"] = "SDSS u"
       tao_bandpass_name["g_SDSS"] = "SDSS g"
       tao_bandpass_name["r_SDSS"] = "SDSS r"
       tao_bandpass_name["i_SDSS"] = "SDSS i"
       tao_bandpass_name["z_SDSS"] = "SDSS z"
       tao_bandpass_name["Y_VISTA"] = "VISTA Y"
       tao_bandpass_name["J_VISTA"] = "VISTA J"
       tao_bandpass_name["H_VISTA"] = "VISTA H"
       tao_bandpass_name["K_VISTA"] = "VISTA K"
       tao_bandpass_name["W1_WISE"] = "WISE1"
       tao_bandpass_name["W2_WISE"] = "WISE2"
       tao_bandpass_name["W3_WISE"] = "WISE3"
       tao_bandpass_name["W4_WISE"] = "WISE4"
       tao_bandpass_name["I1_Spitzer"] = "Spitzer IRAC1"
       tao_bandpass_name["I2_Spitzer"] = "Spitzer IRAC2"
       tao_bandpass_name["I3_Spitzer"] = "Spitzer IRAC3"
       tao_bandpass_name["I4_Spitzer"] = "Spitzer IRAC4"
       tao_bandpass_name["P70_Herschel"] = "Herschel/PACS 70"
       tao_bandpass_name["P100_Herschel"] = "Herschel/PACS 100"
       tao_bandpass_name["P160_Herschel"] = "Herschel/PACS 160"
       header = ""
       # Initialise ordered
       for i in range(0,len(obj.dtype)):
           name = str(obj.dtype.descr[i][0])
           ordered.append(name)
       # process OrderBeforeFieldname
       for i in range(0,len(obj.dtype)):
           name = str(obj.dtype.descr[i][0])
           if "OrderBeforeFieldname" in overrides[name]:
               a_index = get_scraped_order(name)-1
               b_index = get_scraped_order(overrides[name]["OrderBeforeFieldname"])-1
               print("Field[{}]={} Before[{}]={}".format(a_index,ordered[a_index],b_index,ordered[b_index]))
               if a_index < b_index:
                   for ii in range(a_index+1, b_index):
                       ordered[ii-1] = ordered[ii]
                   ordered[b_index-1] = name
               else:
                   for ii in range(a_index-1, b_index-1, -1):
                       print("move [{}]={} to [{}]={}".format(ii,ordered[ii],ii+1,ordered[ii+1]))
                       ordered[ii+1] = ordered[ii]
                   ordered[b_index] = name

       print("I think the following xml is for the hdf5 sidecar xml "+args.magnitude)
       with open("as.xml", "w") as dataxml:
            dataxml.write("  <sageinput>\n")
            for i in range(0,len(obj.dtype)):
                type = str(obj.dtype.descr[i][1])
                if type == "<f8":
                    type = "float"
                if type == "<f4":
                    type = "float"
                if type == "<i4":
                    type = "int"
                if type == "<i8":
                    type = "long long"
                order = str(i+1)
                group = "Galaxy/Halo Properties"
                name = str(obj.dtype.descr[i][0])
                order = str(get_scraped_order(name))
                group = get_scraped_groupname(name, group)
                label = get_scraped_label(name)
                description = get_scraped_description(name)
                units = get_scraped_units(name)
                for agroup in groups.keys():
                    if agroup in name:
                        if name.startswith("dust_"):
                            group = get_scraped_group(agroup)+" (With Dust)"
                        if name.startswith("nodust_"):
                            group = get_scraped_group(agroup)

                dataxml.write("    <Field Type=\""+type+"\"\n")
                dataxml.write("     label=\""+label+"\"\n")
                dataxml.write("     description=\""+description+"\"\n")
                dataxml.write("     order=\""+order+"\"\n")
                dataxml.write("     units=\""+units+"\"\n")
                dataxml.write("     group=\""+group+"\">"+name.lower()+"</Field>\n")
            dataxml.write("  </sageinput>\n")
       print("I think the following xml is for the import process on TAOUI")
       with open("as.ui.txt", "w") as uitxt:
           for i in range(0,len(obj.dtype)):
                #print("i="+str(i))
                type = str(obj.dtype.descr[i][1])
                if type == "<f8":
                    type = "float"
                if type == "<f4":
                    type = "float"
                if type == "<i4":
                    type = "int"
                if type == "<i8":
                    type = "long long"
                order = str(i+1)
                group = "Galaxy/Halo Properties"
                name = str(obj.dtype.descr[i][0])
                order = str(get_scraped_order(name))
                group = get_scraped_groupname(name, group)
                label = get_scraped_label(name)
                units = get_scraped_units(name)
                if units == "":
                    units = "none"
                description = get_scraped_description(name)
                if "OrderBeforeFieldname" in overrides[name]:
                    uitxt.write("fieldname="+name+" label="+label+" units="+units+" description="+description+" group="+group+" OrderBeforeFieldname="+overrides[name]["OrderBeforeFieldname"]+"\n")
                else:
                    uitxt.write("fieldname="+name+" label="+label+" units="+units+" description="+description+" group="+group+"\n")
       with open("as.ui.xml", "w") as uixml:
            uixml.write("<settings>\n")
            uixml.write("  <sageinput>\n")
            j = 0
            very_first_Magnitude_field = True
            for i in range(0,len(obj.dtype)):
                #print("i="+str(i))
                type = str(obj.dtype.descr[i][1])
                if type == "<f8":
                    type = "float"
                if type == "<f4":
                    type = "float"
                if type == "<i4":
                    type = "int"
                if type == "<i8":
                    type = "long long"
                order = str(j+1)
                units = ""
                group = "Galaxy/Halo Properties"
                name = str(obj.dtype.descr[i][0])
                order = str(get_scraped_order(name))
                group = get_scraped_groupname(name, group)
                label = get_scraped_label(name)
                description = get_scraped_description(name)
                units = get_scraped_units(name)
                field = name
                isfield = True
                is_dust_doublet = False
                for agroup in groups.keys():
                    if agroup in name:
                        if name.startswith("dust_"):
                            if very_first_Magnitude_field:
                                very_first_Magnitude_field = False
                                j = get_scraped_order(name) - 1
                                # Note we are assuming from this field forward on all rest of the fields will be "Magnitude" fields
                            is_dust_doublet = True
                            group = "Galaxy Magnitudes"
                            if groups[agroup] == 2:
                                isfield = False
                            groups[agroup] = 2
                            field = get_scraped_group(agroup)+" (With Dust)"
                            label = field
                            description = field
                            break
                        if name.startswith("nodust_"):
                            is_dust_doublet = True
                            group = "Galaxy Magnitudes"
                            if groups[agroup] == 3:
                                isfield = False
                            isfield = False # because we have done it as a doublet
                            groups[agroup] = 3
                            field = get_scraped_group(agroup)
                            label = field
                            description = field
                            break

                if isfield:
                    if not is_dust_doublet:
                        uixml.write("    <Field Type=\""+type+"\"\n")
                        uixml.write("     label=\""+label+"\"\n")
                        uixml.write("     description=\""+description+"\"\n")
                        uixml.write("     order=\""+order+"\"\n")
                        uixml.write("     units=\""+units+"\"\n")
                        uixml.write("     group=\""+group+"\">"+field+"</Field>\n")
                    else:
                        j = j + 1
                        uixml.write("    <Field Type=\""+type+"\"\n")
                        uixml.write("     label=\""+label+"\"\n")
                        uixml.write("     description=\""+description+"\"\n")
                        uixml.write("     order=\""+str(j)+"\"\n")
                        uixml.write("     units=\""+units+"\"\n")
                        uixml.write("     group=\""+group+"\">"+field+"</Field>\n")
                        field = get_scraped_group(agroup)
                        label = field
                        description = field
                        j = j + 1
                        uixml.write("    <Field Type=\""+type+"\"\n")
                        uixml.write("     label=\""+label+"\"\n")
                        uixml.write("     description=\""+description+"\"\n")
                        uixml.write("     order=\""+str(j)+"\"\n")
                        uixml.write("     units=\""+units+"\"\n")
                        uixml.write("     group=\""+group+"\">"+field+"</Field>\n")
            uixml.write("  </sageinput>\n")
            uixml.write("</settings>\n")

if __name__ == '__main__':

   parser = argparse.ArgumentParser(description='Inspect hdf5 file.')
   parser.add_argument('file', type=str, nargs=1, help='hdf5 file')
   parser.add_argument('--magnitude', dest='magnitude', type=str, default="", help='Used as a hint for description of Magnitude fields')
   
   global args
   args = parser.parse_args()
   print(args)
   scrape_metadata()
   f = h5py.File(args.file[0],'r')
   f.visititems(print_attrs)
