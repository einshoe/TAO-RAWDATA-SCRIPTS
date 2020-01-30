import numpy as np
import h5py
import argparse
import sys
import os
import fields_xml

def read_file(file):
    f = h5py.File(file,'r')
    fields = fields_xml.SageSettingsXML("settings.xml")
    print(fields.getNumberOfFields())
    for i in range(0,fields.getNumberOfFields()):
        field = fields.getItem(i)
        print(field.getName()+" type="+field.getType())
    save_snapshot_to_h5(f["Snap037/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap037")
    save_snapshot_to_h5(f["Snap043/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap043")
    save_snapshot_to_h5(f["Snap052/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap052")
    save_snapshot_to_h5(f["Snap063/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap063")
    save_snapshot_to_h5(f["Snap078/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap078")
    save_snapshot_to_h5(f["Snap100/Galaxies"],f['Units'], fields, os.path.splitext(file)[0]+"_Snap100")

def save_snapshot_to_h5(galaxies, units, fields, ofilename):
    bandsuffix3 = ['X', 'Y','Z']
    bandsuffix5 = ['_0', '_1', '_2','_3','_4']
    mydtype = write_sidecar_xml(galaxies, units, fields, ofilename)
    firstcolumn = 0
    lastcolumn = len(galaxies.dtype)-1
    header = ""
    for i in range(firstcolumn,lastcolumn+1):
        header = header + galaxies.dtype.descr[i][0]+","
        #print('dtype=',galaxies.dtype)
    #print(header)
    print("number of galaxies {}".format(galaxies.shape[0]))
    fo = h5py.File(ofilename+'.h5','w')
    odtype = np.dtype(mydtype)
    ogalaxies = fo.create_dataset('Data', galaxies.shape, dtype=odtype)
    oi = 0
    for i in range(firstcolumn,lastcolumn+1):
        if (len(galaxies.dtype.descr[i])==3):
            dataarray = galaxies[galaxies.dtype.descr[i][0]]
            nbands = galaxies.dtype.descr[i][2][0]
            for j in range(0,nbands):
                print("ASSIGN ",ogalaxies.dtype.descr[oi][0]," FROM ",galaxies.dtype.descr[i][0], j)
                ogalaxies[ogalaxies.dtype.descr[oi][0]] = dataarray[:].ravel()[j: :nbands]
                oi = oi+1
        else:
            print("ASSIGN ",ogalaxies.dtype.descr[oi][0]," FROM ",galaxies.dtype.descr[i][0])
            ogalaxies[ogalaxies.dtype.descr[oi][0]] = galaxies[galaxies.dtype.descr[i][0]]
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
    firstcolumn = 0
    lastcolumn = len(galaxies.dtype)-1
    oi = 0
    for i in range(firstcolumn,lastcolumn+1):
        name = galaxies.dtype.descr[i][0]
        unit = ""
        if (galaxies.dtype.descr[i][0] in units.attrs):
            unit = units.attrs[galaxies.dtype.descr[i][0]][0]
        print('unit=',unit,' for ', name)
        if (len(galaxies.dtype.descr[i])==3):
            if (galaxies.dtype.descr[i][2][0]==3):
                for j in range(0,3):
                    oname = name+bandsuffix3[j]
                    oname = oname.lower()

                    field = fields.getFieldWithName(oname)
                    my_type = taodtype(galaxies.dtype.descr[i][1])
                    my_label = oname
                    my_description = name
                    my_order = str(oi+1)
                    my_units = unit
                    my_group = ""
                    if field:
                        my_label = field.getLabel()
                        my_description = field.getDescription()
                        my_order = str(oi+1)
                        my_units = field.getUnits()
                        my_group = field.getGroup()
   
                    mydtype.append((oname, h5dtype(galaxies.dtype.descr[i][1])))
                    outfile.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
                    outfile.write('           label="'+my_label+'"\n')
                    outfile.write('           description="'+my_description+'"\n')
                    outfile.write('           order="'+str(oi+1)+'"\n')
                    outfile.write('           units="'+my_units+'"\n')
                    outfile.write('           group="'+my_group+'">'+oname+"</Field>\n")
                    if my_group != "Internal":
                        outfile_ui.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
                        outfile_ui.write('           label="'+my_label+'"\n')
                        outfile_ui.write('           description="'+my_description+'"\n')
                        outfile_ui.write('           order="'+str(oi+1)+'"\n')
                        outfile_ui.write('           units="'+my_units+'"\n')
                        outfile_ui.write('           group="'+my_group+'">'+oname+"</Field>\n")
                    oi = oi+1
            else:
                for j in range(0,5):
                    oname = name+bandsuffix5[j]
                    oname = oname.lower()

                    field = fields.getFieldWithName(oname)
                    my_type = taodtype(galaxies.dtype.descr[i][1])
                    my_label = oname
                    my_description = name
                    my_order = str(oi+1)
                    my_units = unit
                    my_group = ""
                    if field:
                        my_label = field.getLabel()
                        my_description = field.getDescription()
                        my_order = str(oi+1)
                        my_units = field.getUnits()
                        my_group = field.getGroup()

                    mydtype.append((oname, h5dtype(galaxies.dtype.descr[i][1])))
                    outfile.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
                    outfile.write('           label="'+my_label+'"\n')
                    outfile.write('           description="'+my_description+'"\n')
                    outfile.write('           order="'+str(oi+1)+'"\n')
                    outfile.write('           units="'+my_units+'"\n')
                    outfile.write('           group="'+my_group+'">'+oname+"</Field>\n")
                    if my_group != "Internal":
                        outfile_ui.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
                        outfile_ui.write('           label="'+my_label+'"\n')
                        outfile_ui.write('           description="'+my_description+'"\n')
                        outfile_ui.write('           order="'+str(oi+1)+'"\n')
                        outfile_ui.write('           units="'+my_units+'"\n')
                        outfile_ui.write('           group="'+my_group+'">'+oname+"</Field>\n")
                    oi = oi+1

        else:
            oname = name.lower()

            field = fields.getFieldWithName(oname)
            my_type = taodtype(galaxies.dtype.descr[i][1])
            my_label = oname
            my_description = name
            my_order = str(oi+1)
            my_units = unit
            my_group = "Galaxy Magnitudes"
            if field:
                my_label = field.getLabel()
                my_description = field.getDescription()
                my_order = str(oi+1)
                my_units = field.getUnits()
                if field.getGroup() != "":
                    my_group = field.getGroup()

            mydtype.append((oname, h5dtype(galaxies.dtype.descr[i][1])))
            outfile.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
            outfile.write('           label="'+my_label+'"\n')
            outfile.write('           description="'+my_description+'"\n')
            outfile.write('           order="'+str(oi+1)+'"\n')
            outfile.write('           units="'+my_units+'"\n')
            outfile.write('           group="'+my_group+'">'+oname+"</Field>\n")
            if my_group != "Internal":
                outfile_ui.write('    <Field Type="'+taodtype(galaxies.dtype.descr[i][1])+'"\n')
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
    return 'unknown'

if __name__ == '__main__':
    filename = sys.argv[1]
    #filename = 'meraxes_abs_mags_premade.h5'
    read_file(filename)
