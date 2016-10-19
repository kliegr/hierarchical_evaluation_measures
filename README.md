# Hierarchical evaluation measures
Implementation of hierarchical F-measure (hF), hierarchical precision (hP) and hierarchical recall (hR) and exact precision.
The script was developed for evaluation of type quality in DBpedia.

#Example execution

    python computeHmeasures.py "en.lhd.core.2014.nt" "dbpedia_2014.owl" "gs3-toDBpedia2014.nt" "en.lhd.core.gs3.log"

## Input files - Gold standard datasets

* [en.lhd.core.2014.nt](http://boa.lmcloud.vse.cz/LHD/2014/en.lhd.core.2014.nt.zip)
* [dbpedia_2014.owl](http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/dbpedia_2014.owl.bz2)
* [gs3-toDBpedia2014.nt](http://ner.vse.cz/datasets/linkedhypernyms/gs3-toDBpedia2014.nt)

The datasets are described in our [JWS paper](http://nb.vse.cz/~klit01/papers/lhd2_preprint_web.pdf)

Additional details can be found here [http://ner.vse.cz/datasets/linkedhypernyms/](http://ner.vse.cz/datasets/linkedhypernyms/)
## Output

    reading gs
    reading predicted
    finished reading input datasets
    total instances in groundtruth:1033.0
    total instances in intersection of groundtruth and prediction:402.0
    hP:0.864357864358
    hR:0.370553665326
    hF:0.518726997186
    Precision (exact):0.654228855721


