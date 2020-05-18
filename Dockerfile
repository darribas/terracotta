FROM darribas/gds_py:4.1

ADD ./ $NB_HOME/terracotta
WORKDIR $NB_HOME/terracotta
RUN conda install -c conda-forge -c nodefaults crick
USER root
RUN fix-permissions $NB_HOME/terracotta
USER $NB_UID
RUN pip install -e .[recommended]

# https://github.com/glw/terracotta_cog_docker/blob/master/dockerfile
# Externally accessible data is by default put in /data
WORKDIR /data
# Run as:
# docker run --rm -ti -v /$(pwd)/:/data terracotta
CMD ["/bin/bash"]