import numpy as np
import h5py
import argparse
import sys
import os
import fields_xml

def read_file(file):
    f = h5py.File(file,'r')
    fields = fields_xml.SageSettingsXML("metadata_DRAGONS-X_Tiamat.xml")
    print(fields.getNumberOfFields())
    for i in range(0,fields.getNumberOfFields()):
        field = fields.getItem(i)
        print(field.getName()+" type="+field.getType())
    save_snapshot_to_h5(f["z10pt0"],None, fields, os.path.splitext(file)[0]+"_z10pt0")
    save_snapshot_to_h5(f["z11pt0"],None, fields, os.path.splitext(file)[0]+"_z11pt0")
    save_snapshot_to_h5(f["z12pt0"],None, fields, os.path.splitext(file)[0]+"_z12pt0")
    save_snapshot_to_h5(f["z3pt0"],None, fields, os.path.splitext(file)[0]+"_z3pt0")
    save_snapshot_to_h5(f["z4pt0"],None, fields, os.path.splitext(file)[0]+"_z4pt0")
    save_snapshot_to_h5(f["z5pt0"],None, fields, os.path.splitext(file)[0]+"_z5pt0")
    save_snapshot_to_h5(f["z6pt0"],None, fields, os.path.splitext(file)[0]+"_z6pt0")
    save_snapshot_to_h5(f["z7pt0"],None, fields, os.path.splitext(file)[0]+"_z7pt0")
    save_snapshot_to_h5(f["z8pt0"],None, fields, os.path.splitext(file)[0]+"_z8pt0")
    save_snapshot_to_h5(f["z9pt0"],None, fields, os.path.splitext(file)[0]+"_z9pt0")

def save_snapshot_to_h5(galaxies, units, fields, ofilename):
    nblocks = galaxies.attrs[u'nblocks']
    nrows = galaxies["axis1"].shape[0]
    print("save_snapshot_to_h5 "+ofilename+" has "+str(nblocks)+" blocks each with "+str(nrows))
    print("number of galaxies {}".format(nrows))
    mydtype = write_sidecar_xml(galaxies, units, fields, ofilename)
    fo = h5py.File(ofilename+'.h5','w')
    odtype = np.dtype(mydtype)
    ogalaxies = fo.create_dataset('Data', galaxies["axis1"].shape, dtype=odtype)
    print("ok")
    firstcolumn = 0
    lastcolumn = len(galaxies["axis0"])-1
    oi = 0
    for i in range(0,nblocks):
        blockid = "block"+str(i)+"_items"
        blockidv = "block"+str(i)+"_values"
        print("ASSIGN ",ogalaxies.dtype.descr[oi][0]," FROM ",mydtype[i][0])
        for j in range(0,galaxies[blockidv].shape[1]):
            ogalaxies[ogalaxies.dtype.descr[oi][0]] = galaxies[blockidv][:].transpose()[j]
            oi = oi+1
    fo.close()
def write_sidecar_xml(galaxies, units, fields, ofilename):
    outfile = open(ofilename+'.xml', 'w')
    outfile_ui = open(ofilename+'.ui.xml', 'w')
    outfile.write('<settings>\n')
    outfile_ui.write('<settings>\n')
    outfile.write('  <sageinput>\n')
    outfile_ui.write('  <sageinput>\n')
    bandsuffix3 = ['X', 'Y','Z']
    bandsuffix5 = ['_0', '_1', '_2','_3','_4']

    mydtype = []
    oi = 0
    nblocks = galaxies.attrs[u'nblocks']
    for i in range(0,nblocks):
        blockid = "block"+str(i)+"_items"
        blockidv = "block"+str(i)+"_values"
        print("block id="+str(galaxies[blockid]))
        for j in range(0,galaxies[blockid].shape[0]):
            print("col[{}]={}".format(galaxies[blockid][j],galaxies[blockidv]))
            print(" dt="+str(galaxies[blockidv].dtype))
            name = galaxies[blockid][j]
            oname = name.lower()

            field = fields.getFieldWithName(oname)
            dtypestr = str(galaxies[blockidv].dtype)
            mydtype.append((oname, h5dtype(dtypestr)))

            my_type = taodtype(h5dtype(dtypestr))
            my_label = oname
            my_description = name
            my_order = str(oi+1)
            my_units = ""
            my_group = ""
            if field:
                if field.getLabel():
                    my_label = field.getLabel()
                if field.getDescription():
                    my_description = field.getDescription()
                my_order = str(oi+1)
                if field.getUnits():
                    my_units = field.getUnits()
                if field.getGroup():
                    my_group = field.getGroup()

            outfile.write('    <Field Type="'+my_type+'"\n')
            outfile.write('           label="'+my_label+'"\n')
            outfile.write('           description="'+my_description+'"\n')
            outfile.write('           order="'+str(oi+1)+'"\n')
            outfile.write('           units="'+my_units+'"\n')
            outfile.write('           group="'+my_group+'">'+oname+"</Field>\n")
            if my_group != "Internal":
                outfile_ui.write('    <Field Type="'+my_type+'"\n')
                outfile_ui.write('           label="'+my_label+'"\n')
                outfile_ui.write('           description="'+my_description+'"\n')
                outfile_ui.write('           order="'+str(oi+1)+'"\n')
                outfile_ui.write('           units="'+my_units+'"\n')
                outfile_ui.write('           group="'+my_group+'">'+oname+"</Field>\n")
            oi = oi+1

    outfile.write('  </sageinput>\n')
    outfile_ui.write('  </sageinput>\n')
    outfile.write('</settings>\n')
    outfile_ui.write('</settings>\n')

    return mydtype
def taodtype(dtypestr):
    if (dtypestr == '<i4'):
        return 'int'
    elif (dtypestr == '<i8'):
        return 'long long'
    elif (dtypestr == '<f4'):
        return 'float'
    elif (dtypestr == '<f8'):
        return 'float'
    return 'unknown'

def h5dtype(dtypestr):
    if (dtypestr == '<i4'):
        return '<i4'
    elif (dtypestr == '<i8'):
        return '<i8'
    elif (dtypestr == '<f4'):
        return '<f8'
    elif (dtypestr == '<f8'):
        return '<f8'
    elif (dtypestr == 'float32'):
        return '<f4'
    elif (dtypestr == 'float64'):
        return '<f8'
    elif (dtypestr == 'int32'):
        return '<i4'
    elif (dtypestr == 'int64'):
        return '<i8'
    return 'unknown'

if __name__ == '__main__':
    filename = sys.argv[1]
    #filename = 'meraxes_abs_mags_premade.h5'
    read_file(filename)
