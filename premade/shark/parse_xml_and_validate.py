
import h5py

def sanitise_xml(inxmlfile, outxmlfile):
    with open(inxmlfile,'r') as inxml:
        with open(outxmlfile,'w') as outxml:
            line = inxml.readline()
            while line:
                 yy = line.replace(" & ","&amp;")
                 outxml.write(f"{yy}")
                 line = inxml.readline()
def parse_xml_and_return_fields(xmlfile):
    print(f"start parsing {xmlfile}")
    import re
    mappingBIGFIELD2TAOFIELD = {}
    mappingTAOFIELD2BIGLABEL = {}
    from xml.dom import minidom
    dom = minidom.parse(xmlfile) # needs to be sanitised against "&"
    elements = dom.getElementsByTagName('Field')

    print(f"There are {len(elements)} items:")
    for element in elements:
        print(f"xx [{element.firstChild.nodeValue}]")
        field = str(element.firstChild.nodeValue)
        xx = element.attributes['label'].value
        yy = re.sub("\s\s+", "_", xx)
        yy = yy.replace('  ',"_")
        yy = yy.replace(' ',"_")
        yy = yy.replace('(',"")
        yy = yy.replace(')',"")
        if yy.endswith("nodust"):
            yy = "nodust_"+yy[:-6]
        elif yy.endswith("dust"):
            yy = "dust_"+yy[:-4]
        if 'INTERNAL' in element.attributes['group'].value.upper():
            print(f"This field is not displayed in the GUI: {xx} -> {yy}")
            #break
        else:
            #print(f"{xx} -> {yy}")
            mappingTAOFIELD2BIGLABEL[yy] = xx
            mappingBIGFIELD2TAOFIELD[field] = yy.lower()

    
    print(f"finish parsing {xmlfile}")
    return (mappingBIGFIELD2TAOFIELD,mappingTAOFIELD2BIGLABEL)
        


def test_single_field_between_two_files(shark_file, shark_fieldname,
                                        tao_file, tao_fieldname,
                                        comm=None):
    #if integer type -> exact check
    #np.testing.array_equal()
    try:
        pass
    #    if floating type -> np.testing.array_allclose(shark_file[shark_fieldname],
    #                                              tao_file[tao_fieldname])
    except AssertionError:

        if comm:
            raise MPI_abort()


def create_mapping_between_dtypes(xmlfile):

    (mappingBIGFIELD2TAOFIELD,mappingTAOFIELD2BIGLABEL) = parse_xml_and_return_fields(xmlfile)
    # add "galaxies" prefix to shark
    return (mappingBIGFIELD2TAOFIELD,mappingTAOFIELD2BIGLABEL)

#def compare_two_data_files(, comm=None):
#
#    mapping = get_
#    num_fields = len(mapping.keys())
#    rank = 0
#    ntasks = 1
#    if comm:
#        ntasks = comm.Get_size()
#        rank = comm.Get_rank()
#
#    # mpi parallel loop over num-fields
#    for ...
#        test_single_field_between_two_files()

    # done

if __name__ == "__main__":
    bigdata_xml = "/fred/oz114/kdtao/TAO-RAWDATA-SCRIPTS/premade/shark/shark-combined_APmags.xml"
    sanitised_bigdata_xml = "/fred/oz114/kdtao/TAO-RAWDATA-SCRIPTS/premade/shark/test_compare/sanitised_shark-combined_APmags.xml"
    served_by_tao_xml = "/fred/oz114/kdtao/TAO-RAWDATA-SCRIPTS/premade/shark/test_compare/tao.3185.0.xml"
    sanitised_served_by_tao_xml = "/fred/oz114/kdtao/TAO-RAWDATA-SCRIPTS/premade/shark/test_compare/sanitised.tao.3185.0.xml"
    bigdata_h5 = "/fred/oz114/kdtao/bigdata/shark-combined_APmags.h5"
    served_by_tao_h5 = "/fred/oz114/kdtao/TAO-RAWDATA-SCRIPTS/premade/shark/test_compare/tao.3185.0.hdf5"

    sanitise_xml(bigdata_xml, sanitised_bigdata_xml)
    (mappingBIGFIELD2TAOFIELD,mappingTAOFIELD2BIGLABEL) = create_mapping_between_dtypes(sanitised_bigdata_xml)
    from mpi4py import MPI
    comm = MPI.COMM_WORLD

    f = h5py.File(bigdata_h5, 'r')

    print(f"My rank is {comm.Get_rank()}")
    galaxies = f["galaxies"]
    npts = len(galaxies)
    mydtype = []
    firstcolumn = 0
    lastcolumn = len(galaxies.dtype)-1
    oi = 0
    print("SRC START ========================================= npts=",npts, len(mappingBIGFIELD2TAOFIELD))

    """
    for i in range(firstcolumn,lastcolumn+1):
        name = galaxies.dtype.descr[i][0]
        if name in mappingA:
            print(f"Asrc:{name}:dest:{mappingA[name]}")
        elif name in mappingB:
            print(f"Bsrc:{name}:{mappingB[name]}")
        else:
            print(f"srcNONE:{name}")

    print("DEST START =========================================")
    h = h5py.File(served_by_tao_h5, 'r')
    for name in h.keys():
        #print(f"TO:{name}")
        if name in mappingB:
            print(f"destBsrc:{mappingB[name]}:dest:{name}")
        else:
            print(f"destNONE:{name}")
    """
    # test getting some data
    t = h5py.File(served_by_tao_h5, 'r')
    for j in range(npts):
        if j%10000 == 0:
            print(f"{j} of {npts}")
        for i in range(firstcolumn,lastcolumn+1):
            name = galaxies.dtype.descr[i][0]
            if name in mappingBIGFIELD2TAOFIELD:
                taofield = mappingBIGFIELD2TAOFIELD[name]
                if name == "id_group_sky":
                    print(f"({j},{i}) {name} {taofield}? {t[taofield][j]} == {galaxies[j][i]}?")
                if not t[taofield][j] == galaxies[j][i]:
                    if not name == "id_group_sky":
                        #print(f"problem at ({j},{i}) {name} {taofield}? {t[taofield][j]} == {galaxies[j][i]}")
                        pass




