# -*- coding: utf-8 -*-
import ontospy
import rdflib
from rdflib.namespace import RDF
from ontospy.core.entities import OntoClass
import argparse
import sys
from scrapy.utils.url import canonicalize_url
from rdflib import URIRef
import urllib
import codecs
# INPUTS
# In case of deserialization issues  with prediction file, you may try setting parse_with_rdf_lib to True
# LHD 2014 outputs need to be preprocessed because some uris are malformed (contain space) with
#   cat en.lhd.extension.2015.nt | perl -ne 's/ (?=.*> <http:\/\/[wp])/+/g; print;' > en.lhd.extension.2015.fixed.nt
#  This is fixed in new LHD releases
global g


def get_ancestors_and_self(self):
    ancestors_uris = set([self])
    c = g.getClass(str(self))
    ancestors = c.ancestors()
    for a in ancestors:
        ancestors_uris.add(a.uri)
    return ancestors_uris

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError

def get_most_specific(candidates):
    max_ancestor_count = -1
    best_candidate = ""
    for cand in candidates:
        c = g.getClass(str(cand))
        ancestor_count = len(c.ancestors())
        if ancestor_count > max_ancestor_count:
            best_candidate = cand
            max_ancestor_count = ancestor_count
    return best_candidate


def extract_norm_uri(uric):
    #print uric
    if "\\u" in uric:
        uric=uric.decode('unicode-escape')
    norm = URIRef(canonicalize_url(uric.replace("<","").replace(">","")))
    #print norm
    return norm
    # norm = URIRef(urllib.unquote(uric.replace("<","").replace(">","")))



# This is a faster version, which  first performs filtering of the input file w.r.t. to groundtruth
# Unlike perform_eval, it performs naive manual parsing of the .nt files
def perform_eval(input_file_prediction, input_file_groundtruth, output_file_log, parse_with_rdf_lib=False):
    gs = rdflib.Graph()
    pred = rdflib.Graph()
    if parse_with_rdf_lib:
        gs.parse(input_file_groundtruth, format="nt")
        pred.parse(input_file_prediction, format="nt")
    else:
        gsfile = open(input_file_groundtruth, 'r')

        #gsfile = codecs.open(input_file_groundtruth, encoding='utf-8')
        gs_entities = []
        print "reading gs"
        for s in gsfile:
            stmt = s.split(" ")
            if len(stmt) == 4:
                uri=extract_norm_uri(stmt[0])
                gs.add((uri,RDF.type,extract_norm_uri(stmt[2])))
                gs_entities.append(uri)
        gsfile.close()
        print "reading predicted"
        predicted_file = open(input_file_prediction, 'r')
        #predicted_file = codecs.open(input_file_prediction, encoding='utf-8')
        for s in predicted_file:
            stmt = s.split(" ")
            if len(stmt)==4:
                # This step may be very slow if the predicted file is large
                uri = extract_norm_uri(stmt[0])
                if uri in gs_entities:
                    pred.add((uri,RDF.type,extract_norm_uri(stmt[2])))
        predicted_file.close()
    print ("finished reading input datasets")
    if output_file_log:
        f = open(output_file_log, 'w')
        f.write("subject,gt,predicted\n")
    nominator_sum = 0.0
    totalPh = 0.0
    totalTh = 0.0
    P_exact_match_count = 0.0
    total_instances_with_excluded = 0.0
    total_instances_with_prediction = 0.0
    not_found_in_predicted = set([])
    for subject, predicate, exact_gt in gs:
        try:
            Th = get_ancestors_and_self(exact_gt)
        except Exception as inst:
            print "omitting following - possibly not found in ontology"
            print type(inst)
            print subject
            print exact_gt
            continue
        # get results from evaluated file
        total_instances_with_excluded += 1
        hits = pred.objects(subject, RDF.type)
        Ph = set([])

        for hit in hits:
            # filter out other than DBpedia ontology
            if type(g.getClass(str(hit))) == OntoClass:
                # add superclasses, double additions are automatically resolved, since we use set
                Ph = set.union(Ph, get_ancestors_and_self(hit))
        if len(Ph) > 0:
            total_instances_with_prediction += 1
            most_specific = get_most_specific(Ph)
            if exact_gt == most_specific:
                    P_exact_match_count += 1
            if output_file_log:
                f.write((subject + "," + exact_gt + "," + most_specific + "\n").encode('utf-8'))
        else:
            not_found_in_predicted.add(subject)
        nominator_sum += len(Th.intersection(Ph))
        totalPh +=  len(Ph)
        totalTh += len(Th)
    if output_file_log:
        f.close()
    hP = nominator_sum / totalPh
    hR = nominator_sum / totalTh
    hF = (2 * hP * hR) / (hP + hR)
    acc =     P_exact_match_count / total_instances_with_prediction
    print "instances from gold standard not found in predicted:" + ','.join([e.title() for e in not_found_in_predicted])
    print "total instances in groundtruth:" + str(total_instances_with_excluded)
    print "total instances in intersection of groundtruth and prediction:" + str(total_instances_with_prediction)
    print "hP:" + str(hP)
    print "hR:" + str(hR)
    print "hF:" + str(hF)
    print "Precision (exact):" + str(acc)
    print " Warning: this metric is not relevant for evaluations where prediction output contains multiple  most specific types"
    return acc, hP,hR,hF


def init_ontology(input_file_ontology):
    global g
    g = ontospy.Graph(input_file_ontology)

parser = argparse.ArgumentParser(description='Compute hierarchical measures.')
parser.add_argument('input_file_prediction', type=str, nargs='?')  # default="instance_types_en.gs1.nt",
parser.add_argument('input_file_ontology', type=str, nargs='?')  # default="dbpedia_2014.owl"
parser.add_argument('input_file_groundtruth', type=str, nargs='?')  # default="gs1-toDBpedia2014.nt"
parser.add_argument('output_file_log', type=str, nargs='?', default="default.log")  
parser.add_argument('parse_with_rdf_lib', type=str, nargs='?', default="False")
args = parser.parse_args()


print sys.argv
if len(sys.argv) > 2:
    print args
    init_ontology(args.input_file_ontology)
    perform_eval(args.input_file_prediction, args.input_file_groundtruth, args.output_file_log, str_to_bool(args.parse_with_rdf_lib))
    # perform_eval("hSVMinputFiles/gs1-hSVM22.nt","dbpedia_2014.owl","gs1-toDBpedia2014.nt","instance_types_en.gs1.log", False)

