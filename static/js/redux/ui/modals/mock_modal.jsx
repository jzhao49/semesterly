import PropTypes from 'prop-types';
import React from 'react';
import Modal from 'boron/FadeModal';
import * as SemesterlyPropTypes from '../../constants/semesterlyPropTypes';

class MockModal extends React.Component {

  componentDidUpdate() {
    if (this.props.isVisible) {
      this.modal.show();
    }
  }

  render() {
    const modalHeader =
      (<div className="modal-content">
        <div className="modal-header">
          <h1>Mock Modal!</h1>
        </div>
      </div>);
    const modalStyle = {
      width: '100%',
    };
    return (
      <Modal
        ref={(c) => { this.modal = c; }}
        className="mock-modal max-modal"
        modalStyle={modalStyle}
        onHide={this.props.toggleMockModal}
      >
        <div className="modal-content">
          <div className="modal-header">
            <h1>Mock Modal!</h1>
          </div>
          <div className="modal-body">
            <span>First Name: {this.props.mockUser.mockUserFirstName} </span>
            <span>Last Name: {this.props.mockUser.mockUserLastName} </span>
            <span>Graduating Class: {this.props.mockUser.mockUserYear} </span>
          </div>
        </div>
      </Modal>
    );
  }
}

MockModal.propTypes = {
  mockUser: SemesterlyPropTypes.mockUser.isRequired,
  userInfo: SemesterlyPropTypes.userInfo.isRequired,
  toggleMockModal: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
};

export default MockModal;
