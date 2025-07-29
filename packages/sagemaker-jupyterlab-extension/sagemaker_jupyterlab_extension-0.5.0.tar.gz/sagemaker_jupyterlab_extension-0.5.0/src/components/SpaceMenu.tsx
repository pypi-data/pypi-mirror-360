import React, { FC } from 'react';
import LanguageIcon from '@mui/icons-material/Language';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

import { il18Strings, COOKIE_NAMES, spaceTestIds } from '../constants';
import styles from './styles/SpaceMenuStyles';
import { getCookie } from '../utils/sessionManagerUtils';

const { unknownSpace, unknownUser } = il18Strings.Space;

interface SpaceMenuProps {
  spaceName: string | undefined;
}

const SpaceMenu: FC<SpaceMenuProps> = ({ spaceName }) => {
  const isSpaceNameAvailable = !!spaceName;
  const userProfileName = getCookie(COOKIE_NAMES.USER_PROFILE_NAME);

  return (
    <div className={styles.SpaceMenuHeader} data-testid={spaceTestIds.menu.header}>
      {isSpaceNameAvailable ? <LanguageIcon fontSize="small" /> : <AccountCircleIcon fontSize="small" />}
      <p>{`${(userProfileName && userProfileName[1]) || unknownUser} / ${
        isSpaceNameAvailable ? spaceName : unknownSpace
      }`}</p>
    </div>
  );
};

export { SpaceMenu };
