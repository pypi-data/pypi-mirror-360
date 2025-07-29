# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""High-level interface for dataset creation

"""

import random
import uuid
from collections.abc import Mapping
from typing import Any

#from os import listdir
#from datalad import _seed
#from datalad.support.constraints import (
#    EnsureStr,
#    EnsureNone,
#    EnsureKeyChoice,
#)
from datalad_core.commands import (
    EnsureDataset,
    JointParamProcessor,
    ParamSetConstraint,
    datalad_command,
)
from datalad_core.constraints import (
    EnsureChoice,
    EnsurePath,
)


class EnsureParentDatasetConditions(ParamSetConstraint):
    input_synopsis = 'existing parent dataset without content conflict'

    def __init__(self):
        # announce which args will be validated
        super().__init__(('dataset', 'path'))

    def __call__(self, val: Mapping[str, Any]) -> Mapping[str, Any]:
        if val['dataset'].pristine_spec is None:
            # no dataset was given. nothing to check
            return val

        # TODO: check for existence of parent repo
        # TODO: check for collisions with parent repo content
        return val


class EnsureAnnexParams(ParamSetConstraint):
    input_synopsis = 'coherent annex parameters'

    def __init__(self):
        # announce which args will be validated
        super().__init__(('annex', 'annex_description'))

    def __call__(self, val: Mapping[str, Any]) -> Mapping[str, Any]:
        if val['annex'] is False and val['annex_description']:
            self.raise_for(
                val,
                'cannot assign an annex description with no annex',
            )
        return val


@datalad_command(
    preproc=JointParamProcessor(
        {
            'dataset': EnsureDataset(),
            'path': EnsurePath(),
            'annex': EnsureChoice(
                # no annex
                False,
                # standard annex
                True,
                # private-mode annex
                'private',
            ),
        },
        proc_defaults={'dataset', 'path'},
        tailor_for_dataset={
            'path': 'dataset',
        },
        paramset_constraints=(
            EnsureAnnexParams(),
            EnsureParentDatasetConditions(),
        ),
    ),
)
def create_dataset(
    path=None,
    *,
    dataset=None,
    annex=True,
    annex_description=None,
    #initopts=None,
    #force=False,
    #cfg_proc=None
):
    return []


def dummy():
    # two major cases
    # 1. we got a `dataset` -> we either want to create it (path is None),
    #    or another dataset in it (path is not None)
    # 2. we got no dataset -> we want to create a fresh dataset at the
    #    desired location, either at `path` or PWD
    if (isinstance(initopts, (list, tuple)) and '--bare' in initopts) or (
            isinstance(initopts, dict) and 'bare' in initopts):
        raise ValueError(
            "Creation of bare repositories is not supported. Consider "
            "one of the create-sibling commands, or use "
            "Git to init a bare repository and push an existing dataset "
            "into it.")

    # assure cfg_proc is a list (relevant if used via Python API)
    cfg_proc = ensure_list(cfg_proc)

    # prep for yield
    res = dict(action='create', path=str(path),
               logger=lgr, type='dataset',
               refds=refds_path)

    refds = None
    if refds_path and refds_path != str(path):
        refds = require_dataset(
            refds_path, check_installed=True,
            purpose='create a subdataset')

        path_inrefds = path_under_rev_dataset(refds, path)
        if path_inrefds is None:
            yield dict(
                res,
                status='error',
                message=(
                    "dataset containing given paths is not underneath "
                    "the reference dataset %s: %s",
                    ds, str(path)),
            )
            return

    # try to locate an immediate parent dataset
    # we want to know this (irrespective of whether we plan on adding
    # this new dataset to a parent) in order to avoid conflicts with
    # a potentially absent/uninstalled subdataset of the parent
    # in this location
    # it will cost some filesystem traversal though...
    parentds_path = get_dataset_root(
        op.normpath(op.join(str(path), os.pardir)))
    if parentds_path:
        prepo = GitRepo(parentds_path)
        parentds_path = Path(parentds_path)
        # we cannot get away with a simple
        # GitRepo.get_content_info(), as we need to detect
        # uninstalled/added subdatasets too
        check_path = Path(path)
        pstatus = prepo.status(
            untracked='no',
            # limit query to target path for a potentially massive speed-up
            paths=[check_path.relative_to(parentds_path)])
        if (pstatus.get(check_path, {}).get('type') != 'dataset' and
            any(check_path == p or check_path in p.parents
                for p in pstatus)):
            # redo the check in a slower fashion, it is already broken
            # let's take our time for a proper error message
            conflict = [
                p for p in pstatus
                if check_path == p or check_path in p.parents]
            res.update({
                'status': 'error',
                'message': (
                    'collision with content in parent dataset at %s: %s',
                    str(parentds_path),
                    [str(c) for c in conflict])})
            yield res
            return
        if not force:
            # another set of check to see whether the target path is pointing
            # into a known subdataset that is not around ATM
            subds_status = {
                parentds_path / k.relative_to(prepo.path)
                for k, v in pstatus.items()
                if v.get('type', None) == 'dataset'}
            check_paths = [check_path]
            check_paths.extend(check_path.parents)
            if any(p in subds_status for p in check_paths):
                conflict = [p for p in check_paths if p in subds_status]
                res.update({
                    'status': 'error',
                    'message': (
                        'collision with %s (dataset) in dataset %s',
                        str(conflict[0]),
                        str(parentds_path))})
                yield res
                return

    # important to use the given Dataset object to avoid spurious ID
    # changes with not-yet-materialized Datasets
    tbds = ds if isinstance(ds, Dataset) and \
        ds.path == path else Dataset(str(path))

    # don't create in non-empty directory without `force`:
    if op.isdir(tbds.path) and listdir(tbds.path) != [] and not force:
        res.update({
            'status': 'error',
            'message':
                'will not create a dataset in a non-empty directory, use '
                '`--force` option to ignore'})
        yield res
        return

    # Check if specified cfg_proc(s) can be discovered, storing
    # the results so they can be used when the time comes to run
    # the procedure. If a procedure cannot be found, raise an
    # error to prevent creating the dataset.
    cfg_proc_specs = []
    if cfg_proc:
        discovered_procs = tbds.run_procedure(
            discover=True,
            result_renderer='disabled',
            return_type='list',
        )
        for cfg_proc_ in cfg_proc:
            for discovered_proc in discovered_procs:
                if discovered_proc['procedure_name'] == 'cfg_' + cfg_proc_:
                    cfg_proc_specs.append(discovered_proc)
                    break
            else:
                raise ValueError("Cannot find procedure with name "
                                 "'%s'" % cfg_proc_)

    if initopts is not None and isinstance(initopts, list):
        initopts = {'_from_cmdline_': initopts}

    # Note for the code below:
    # OPT: be "smart" and avoid re-resolving .repo -- expensive in DataLad
    # Reuse tbrepo instance, do not use tbds.repo

    # create and configure desired repository
    # also provides initial set of content to be tracked with git (not annex)
    if no_annex:
        tbrepo, add_to_git = _setup_git_repo(path, initopts, fake_dates)
    else:
        tbrepo, add_to_git = _setup_annex_repo(
            path, initopts, fake_dates, description)

    # OPT: be "smart" and avoid re-resolving .repo -- expensive in DataLad
    # Note, must not happen earlier (before if) since "smart" it would not be
    tbds_config = tbds.config

    # record an ID for this repo for the afterlife
    # to be able to track siblings and children
    id_var = 'datalad.dataset.id'
    # Note, that Dataset property `id` will change when we unset the
    # respective config. Therefore store it before:
    tbds_id = tbds.id
    if id_var in tbds_config:
        # make sure we reset this variable completely, in case of a
        # re-create
        tbds_config.unset(id_var, scope='branch')

    if _seed is None:
        # just the standard way
        # use a fully random identifier (i.e. UUID version 4)
        uuid_id = str(uuid.uuid4())
    else:
        # Let's generate preseeded ones
        uuid_id = str(uuid.UUID(int=random.getrandbits(128)))
    tbds_config.add(
        id_var,
        tbds_id if tbds_id is not None else uuid_id,
        scope='branch',
        reload=False)

    # make config overrides permanent in the repo config
    # this is similar to what `annex init` does
    # we are only doing this for config overrides and do not expose
    # a dedicated argument, because it is sufficient for the cmdline
    # and unnecessary for the Python API (there could simply be a
    # subsequence ds.config.add() call)
    for k, v in tbds_config.overrides.items():
        tbds_config.add(k, v, scope='local', reload=False)

    # all config manipulation is done -> fll reload
    tbds_config.reload()

    # must use the repo.pathobj as this will have resolved symlinks
    add_to_git[tbrepo.pathobj / '.datalad'] = {
        'type': 'directory',
        'state': 'untracked'}

    # save everything, we need to do this now and cannot merge with the
    # call below, because we may need to add this subdataset to a parent
    # but cannot until we have a first commit
    tbrepo.save(
        message='[DATALAD] new dataset',
        git=True,
        # we have to supply our own custom status, as the repo does
        # not have a single commit yet and the is no HEAD reference
        # TODO make `GitRepo.status()` robust to this state.
        _status=add_to_git,
    )

    for cfg_proc_spec in cfg_proc_specs:
        yield from tbds.run_procedure(
            cfg_proc_spec,
            result_renderer='disabled',
            return_type='generator',
        )

    # the next only makes sense if we saved the created dataset,
    # otherwise we have no committed state to be registered
    # in the parent
    if isinstance(refds, Dataset) and refds.path != tbds.path:
        # we created a dataset in another dataset
        # -> make submodule
        yield from refds.save(
            path=tbds.path,
            return_type='generator',
            result_renderer='disabled',
        )
    else:
        # if we do not save, we touch the root directory of the new
        # dataset to signal a change in the nature of the directory.
        # this is useful for apps like datalad-gooey (or other
        # inotify consumers) to pick up on such changes.
        tbds.pathobj.touch()

    res.update({'status': 'ok'})
    yield res


def _setup_git_repo(path, initopts=None, fake_dates=False):
    """Create and configure a repository at `path`

    Parameters
    ----------
    path: str or Path
      Path of the repository
    initopts: dict, optional
      Git options to be passed to the GitRepo constructor
    fake_dates: bool, optional
      Passed to the GitRepo constructor

    Returns
    -------
    GitRepo, dict
      Created repository and records for any repo component that needs to be
      passed to git-add as a result of the setup procedure.
    """
    tbrepo = GitRepo(
        path,
        create=True,
        create_sanity_checks=False,
        git_opts=initopts,
        fake_dates=fake_dates)
    # place a .noannex file to indicate annex to leave this repo alone
    stamp_path = Path(tbrepo.path) / '.noannex'
    stamp_path.touch()
    add_to_git = {
        stamp_path: {
            'type': 'file',
            'state': 'untracked',
        }
    }
    return tbrepo, add_to_git


def _setup_annex_repo(path, initopts=None, fake_dates=False,
                      description=None):
    """Create and configure a repository at `path`

    This includes a default setup of annex.largefiles.

    Parameters
    ----------
    path: str or Path
      Path of the repository
    initopts: dict, optional
      Git options to be passed to the AnnexRepo constructor
    fake_dates: bool, optional
      Passed to the AnnexRepo constructor
    description: str, optional
      Passed to the AnnexRepo constructor

    Returns
    -------
    AnnexRepo, dict
      Created repository and records for any repo component that needs to be
      passed to git-add as a result of the setup procedure.
    """
    # always come with annex when created from scratch
    tbrepo = AnnexRepo(
        path,
        create=True,
        create_sanity_checks=False,
        # do not set backend here, to avoid a dedicated commit
        backend=None,
        # None causes version to be taken from config
        version=None,
        description=description,
        git_opts=initopts,
        fake_dates=fake_dates
    )
    # set the annex backend in .gitattributes as a staged change
    tbrepo.set_default_backend(
        cfg.obtain('datalad.repo.backend'),
        persistent=True, commit=False)
    add_to_git = {
        tbrepo.pathobj / '.gitattributes': {
            'type': 'file',
            'state': 'added',
        }
    }
    # make sure that v6 annex repos never commit content under .datalad
    attrs_cfg = (
        ('config', 'annex.largefiles', 'nothing'),
    )
    attrs = tbrepo.get_gitattributes(
        [op.join('.datalad', i[0]) for i in attrs_cfg])
    set_attrs = []
    for p, k, v in attrs_cfg:
        if attrs.get(op.join('.datalad', p), {}).get(k, None) != v:
            set_attrs.append((p, {k: v}))
    if set_attrs:
        tbrepo.set_gitattributes(
            set_attrs,
            attrfile=op.join('.datalad', '.gitattributes'))

    # prevent git annex from ever annexing .git* stuff (gh-1597)
    attrs = tbrepo.get_gitattributes('.git')
    if attrs.get('.git', {}).get('annex.largefiles', None) != 'nothing':
        tbrepo.set_gitattributes([
            ('**/.git*', {'annex.largefiles': 'nothing'})])
        # must use the repo.pathobj as this will have resolved symlinks
        add_to_git[tbrepo.pathobj / '.gitattributes'] = {
            'type': 'file',
            'state': 'untracked'}
    return tbrepo, add_to_git
